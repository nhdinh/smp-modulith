#!/usr/bin/env python
# -*- coding: utf-8 -*-
import uuid
from typing import Set, List, Union, Any, Optional

from foundation.events import EventMixin
from foundation.value_objects.address import LocationAddress
from foundation.value_objects.factories import get_money
from store.adapter.id_generators import STORE_SUPPLIER_ID_PREFIX, generate_warehouse_id
from store.application.usecases.const import ExceptionMessages, ThingGoneInBlackHoleError
from store.domain.entities.setting import Setting
from store.domain.entities.store_address import StoreAddress, StoreAddressType
from store.domain.entities.store_catalog import StoreCatalog
from store.domain.entities.store_collection import StoreCollection
from store.domain.entities.store_owner import StoreOwner
from store.domain.entities.store_product import StoreProduct
from store.domain.entities.store_product_brand import StoreProductBrand
from store.domain.entities.store_product_tag import StoreProductTag
from store.domain.entities.store_supplier import StoreSupplier
from store.domain.entities.store_warehouse import StoreWarehouse
from store.domain.entities.value_objects import StoreId, StoreCatalogId, StoreSupplierId, StoreAddressId
from store.domain.events.store_created_event import StoreCreatedEvent
from store.domain.events.store_product_events import StoreProductCreatedEvent, StoreProductUpdatedEvent


class Store(EventMixin):
    def __init__(self, store_id: StoreId, store_name: str, store_owner: StoreOwner, version: int = 0,
                 settings: List[Setting] = None) -> None:
        super(Store, self).__init__()

        self.store_id = store_id
        self.name = store_name
        self.version = version

        if store_owner is not None:
            self._store_owner = store_owner
            self.owner_email = store_owner.email
            self._owner_id = store_owner.id
        else:
            raise Exception(ExceptionMessages.FAILED_TO_CREATE_STORE_NO_OWNER)

        if settings:
            self._settings = settings
        else:
            self._settings = self._default_settings

        self._managers = set()  # type: Set

        # children data
        self._addresses = set()  # type:Set[StoreAddress]
        self._warehouses = set()  # type: Set[StoreWarehouse]
        self._brands = set()  # type: Set[StoreProductBrand]
        self._suppliers = set()  # type:Set[StoreSupplier]
        self._catalogs = set()  # type: Set[StoreCatalog]
        self._collections = set()  # type: Set[StoreCollection]
        self._products = set()  # type: Set[StoreProduct]

    # region ## Properties ##
    @property
    def settings(self) -> Set[Setting]:
        return set() if self._settings is None else self._settings

    @property
    def warehouses(self) -> Set[StoreWarehouse]:
        return self._warehouses

    @property
    def addresses(self) -> Set[StoreAddress]:
        return self._addresses

    @property
    def catalogs(self) -> Set[StoreCatalog]:
        return self._catalogs

    @property
    def products(self) -> Set[StoreProduct]:
        return self._products

    @property
    def suppliers(self) -> Set[StoreSupplier]:
        return self._suppliers

    @property
    def default_warehouse(self) -> Optional[StoreWarehouse]:
        try:
            default_warehouse = next(w for w in self._warehouses if w.default)
            return default_warehouse
        except StopIteration:
            return None

    @property
    def brands(self) -> Set[StoreProductBrand]:
        return self._brands

    def get_setting(self, key: str, default_value: Any = None):
        try:
            setting = next(s for s in self._settings if s.key == key)
            return setting.value
        except StopIteration:
            return default_value

    def has_setting(self, key: str):
        return self.get_setting(key=key, default_value=None) is not None

    def update_setting(self, key: str, value: str):
        try:
            setting = next(s for s in self._settings if s.key == key)

            # check type

            # set value
            setting.value = value
        except StopIteration:
            raise Exception('Update store setting failed')

    @property
    def _default_settings(self) -> Set[Setting]:
        _settings = set()  # type: Set[Setting]
        _settings.add(Setting('default_page_size', '10', 'int'))
        _settings.add(Setting('default_catalog_reference', 'unassigned_catalog', 'str'))
        _settings.add(Setting('default_catalog_display_name', 'Chưa phân loại', 'str'))
        _settings.add(Setting('default_collection_reference', 'unassigned_collection', 'str'))
        _settings.add(Setting('default_collection_display_name', 'Chưa phân loại', 'str'))
        _settings.add(Setting('default_currency', 'VND', 'str'))

        return _settings

    @property
    def store_owner(self) -> StoreOwner:
        return self._store_owner

    # endregion

    # region ## Creating new store ##
    @classmethod
    def create_store_from_registration(cls, store_id: StoreId, store_name: str, store_owner: StoreOwner) -> "Store":
        # create the store from registration data
        store = Store(
            store_id=store_id,
            store_name=store_name,
            store_owner=store_owner
        )

        # raise event
        store._record_event(StoreCreatedEvent(store.store_id, store.name, store.store_owner.email, store.owner_email))

        return store

    # endregion

    # region ## Products Management ##
    def create_product(self,
                       title: str,
                       sku: str,
                       default_unit: str,
                       **kwargs) -> StoreProduct:
        # check if any product with this title exists
        try:
            product_with_such_title = next(p for p in self._products if p.title.lower() == title.strip().lower())
            if product_with_such_title:
                raise Exception(ExceptionMessages.STORE_PRODUCT_EXISTED)
        except StopIteration:
            pass

        # image
        image = ''
        image_str = kwargs.get('image')
        if image_str:
            image = image_str

        # process input data: StoreProductBrand
        brand = None
        brand_str = kwargs.get('brand')
        if brand_str:
            brand = self._brand_factory(name=brand_str)

        # process input data: StoreSupplier
        suppliers = []
        purchase_price_list = []
        supplier_list = kwargs.get('suppliers')
        if supplier_list:
            for input_supplier_str in supplier_list:
                purchase_price_list += input_supplier_str['supplier_prices'] if type(
                    input_supplier_str['supplier_prices']) is list else [input_supplier_str['supplier_prices']]

                supplier = self._supplier_factory(supplier_name=input_supplier_str['supplier_name'],
                                                  contact_name=input_supplier_str['contact_name'],
                                                  contact_phone=input_supplier_str['contact_phone'])

                suppliers.append(supplier)

        # process input data: StoreCatalog
        catalog_str = kwargs.get('catalog')
        if catalog_str:
            catalog = self._make_catalog(title=catalog_str)
        else:
            catalog = self._default_catalog_factory()

        # process input data: StoreCollections
        collections = []
        collection_str_list = kwargs.get('collections')
        if collection_str_list:
            collection_str_list = collection_str_list if type(collection_str_list) is list else [collection_str_list]
            collections = [self._collection_factory(title=col, parent_catalog=catalog) for col in collection_str_list]

        # threshold
        restock_threshold, max_stock_threshold = 0, 0
        restock_th_str = kwargs.get('restock_threshold')
        max_stock_th_str = kwargs.get('max_stock_threshold')
        try:
            restock_threshold = int(restock_th_str)
        except:
            restock_threshold = -1

        try:
            max_stock_threshold = int(max_stock_th_str)
        except:
            max_stock_threshold = -1

        # process input data: Tags
        tags = kwargs.get('tags')
        if tags:
            self.append_tags_stack(tags)

        # make product
        store_product = StoreProduct.create_product(
            title=title,
            sku=sku,
            image=image,
            default_unit=default_unit,
            restock_threshold=restock_threshold,
            max_stock_threshold=max_stock_threshold,
            store=self,
            brand=brand,
            catalog=catalog,
            collections=collections,
            suppliers=suppliers,
            tags=tags
        )

        # process input data: StoreProductUnit (which are unit conversions)
        unit_conversions = kwargs.get('unit_conversions')
        for unit_conversion in unit_conversions:
            store_product.create_unit(unit_name=unit_conversion['unit'],
                                      conversion_factor=unit_conversion['conversion_factor'],
                                      base_unit=unit_conversion['base_unit'])

        # process input data: PurchasePrices
        default_currency = self.get_setting('default_currency', 'VND')
        for price in purchase_price_list:
            store_product.create_purchase_price_by_supplier(
                supplier=self._supplier_factory(supplier_name=price['supplier_name']),
                unit=store_product.get_unit(price['unit']),
                price=get_money(amount=price['price'],
                                currency_str=price['currency'] if 'currency' in price.keys() and price[
                                    'currency'] is not None else default_currency),
                tax=price['tax'],
                effective_from=price['effective_from'],
            )

        # add to catalog
        self._append_product(store_product)

        # build the array of stocking quantity
        units = [u.unit_name for u in store_product.units]
        first_stockings_input = kwargs.get('first_inventory_stocking_for_unit_conversions')
        first_stockings_input = {item['unit']: item['stocking'] for item in first_stockings_input}

        # raise event
        self._record_event(StoreProductCreatedEvent(
            product_id=store_product.product_id,
            default_unit=store_product.default_unit.unit_name,
            units=units,
            first_stocks=[first_stockings_input.get(u, 0) for u in units]
        ))

        return store_product

    def _append_product(self, product: StoreProduct):
        self._products.add(product)

    # endregion

    def _brand_factory(self, name: str) -> StoreProductBrand:
        try:
            brand = next(b for b in self._brands if b.name.lower() == name.strip().lower())
            return brand
        except StopIteration:
            brand = StoreProductBrand(name=name)
            self._brands.add(brand)
            return brand

    def _supplier_factory(self, supplier_name: str, contact_name: str = None, contact_phone: str = None):
        try:
            # contact = SupplierContact(contact_name=contact_name, contact_phone=contact_phone)
            supplier = next(s for s in self._suppliers if s.supplier_name.lower() == supplier_name.strip().lower())
            # if contact not in supplier.contacts:
            #     supplier.contacts.add(contact)

            return supplier
        except StopIteration:
            # contact = SupplierContact(contact_name=contact_name, contact_phone=contact_phone)
            supplier = StoreSupplier(supplier_name=supplier_name,
                                     contact_name=contact_name,
                                     contact_phone=contact_phone)
            # , contacts=set([contact]))
            self._suppliers.add(supplier)
            return supplier

    def _is_collection_exists(self, title: str, parent_catalog: StoreCatalog):
        try:
            collection = next(
                c for c in self._collections if c.title == title and c.catalog == parent_catalog)
            if collection:
                return True
        except StopIteration:
            return False

    def _collection_factory(self, title: str, parent_catalog: StoreCatalog) -> StoreCollection:
        try:
            collection = next(coll for coll in self._collections if
                              coll.title.lower() == title.strip().lower() and coll.catalog == parent_catalog)
            return collection
        except StopIteration:
            collection = self.make_collection(title=title, parent_catalog=parent_catalog)
            self._collections.add(collection)
            return collection

    def make_collection(self, title: str, parent_catalog: StoreCatalog, **kwargs) -> StoreCollection:
        title = title.strip()

        try:
            collection = next(
                c for c in self._collections if c.title.lower() == title.lower() and c.catalog == parent_catalog)

            if collection:
                return collection
        except StopIteration:
            # make collection
            is_default = kwargs.get('default')
            if is_default is None:
                is_default = False

            collection = StoreCollection(title=title, default=is_default)
            parent_catalog.collections.add(collection)
            self._collections.add(collection)

            return collection

    def _make_catalog(self, title: str) -> StoreCatalog:
        try:
            catalog = next(c for c in self._catalogs if c.title.lower() == title.strip().lower())
            return catalog
        except StopIteration:
            catalog = self.create_catalog(title=title)
            self._catalogs.add(catalog)
            return catalog

    def _default_catalog_factory(self):
        """
        Get or create a default catalog of the Store

        :return: an instance of the catalog
        """
        try:
            catalog = next(c for c in self._catalogs if c.default)
            return catalog
        except StopIteration:
            catalog = self._create_default_catalog()
            self._catalogs.add(catalog)
            return catalog

    def create_catalog(self, title: str, **kwargs) -> StoreCatalog:
        """
        Create a `StoreCatalog` instance

        :param title: title of the catalog
        :param kwargs: may contains `reference`, `default`
        :return: an instance of the `StoreCatalog`
        """
        is_default = kwargs.get('default')
        if is_default is None:
            is_default = False

        # make catalog
        catalog = StoreCatalog(title=title, default=is_default)

        # make default collection

        return catalog

    def _create_default_catalog(self) -> StoreCatalog:
        """
        Create a default `StoreCatalog` instance

        :return: an instance of the `StoreCatalog`
        """
        catalog_reference = self.get_setting('default_catalog_reference', 'unassigned_catalog')
        catalog_title = self.get_setting('default_catalog_title', 'Catalog')
        is_default = True

        return self.create_catalog(reference=catalog_reference, title=catalog_title, default=is_default)

    def turn_on_default_catalog(self, catalog_id: StoreCatalogId) -> bool:
        try:
            catalog = next(c for c in self.catalogs if c.catalog_id == catalog_id)
            catalog.default = True
            return True
        except StopIteration:
            return False

    def is_catalog_exists(self, title: str) -> bool:
        title = title.strip()
        try:
            c = next(c for c in self._catalogs if c.title.lower() == title.lower())
            if c:
                return True
        except StopIteration:
            return False
        else:
            return False

    def append_tags_stack(self, tags: List[StoreProductTag]):
        pass

    # region ## Internal class method ##
    def __str__(self) -> str:
        return f'<Store #{self.store_id} name="{self.name}" >'

    def __eq__(self, other) -> bool:
        return isinstance(other, Store) and self.store_id == other.store_id

    # endregion
    def create_warehouse(self, warehouse_name: str):
        if len(self._warehouses) >= 1:
            raise Exception('Sorry. This version of application only allow to create 01 warehouse per store.')

        """
        Create a new warehouse for this store

        :param warehouse_name: name of the warehouse
        :return: instance of the warehouse
        """
        return StoreWarehouse(
            warehouse_id=generate_warehouse_id(),
            store_id=self.store_id,
            warehouse_owner=self.owner_email,
            warehouse_name=warehouse_name,
            default=False,
            disabled=False
        )

    # def contains_catalog_reference(self, catalog_reference: StoreCatalogReference):
    #     try:
    #         catalog = next(c for c in self.catalogs if c.reference == catalog_reference)
    #         if catalog:
    #             return True
    #     except StopIteration:
    #         return False

    def add_address(self, recipient: str, phone: str, address: LocationAddress):
        try:
            store_address = StoreAddress(
                recipient=recipient,
                phone=phone,
                address_type=StoreAddressType.STORE_ADDRESS,
                location_address=address,
            )

            # set cache attributes, use ORM event when persistence is better
            setattr(store_address, '_street_address', address.street_address)
            setattr(store_address, '_sub_division_name', address.sub_division.sub_division_name)
            setattr(store_address, '_division_name', address.division.division_name)
            setattr(store_address, '_city_name', address.city.city_name)
            setattr(store_address, '_country_name', address.country.country_name)
            setattr(store_address, '_iso_code', address.country.iso_code)
            setattr(store_address, '_postal_code', address.postal_code)

            self.addresses.add(store_address)
        except Exception as exc:
            raise exc

    def get_address(self, address_id: StoreAddressId):
        try:
            address = next(a for a in self._addresses if a.store_address_id == address_id)
            return address
        except StopIteration:
            return None

    def get_supplier(self, supplier_id_or_name: Union[StoreSupplierId, str]):
        try:
            if isinstance(supplier_id_or_name, str) and supplier_id_or_name.startswith(STORE_SUPPLIER_ID_PREFIX):
                supplier = next(s for s in self._suppliers if s.supplier_id == supplier_id_or_name)
                return supplier
            elif isinstance(supplier_id_or_name, str):
                supplier = next(s for s in self._suppliers if s.supplier_name == supplier_id_or_name)
                return supplier
            else:
                raise TypeError
        except StopIteration:
            return None

    def update_product(self, product: StoreProduct, **kwarg):
        items_being_updated = []

        brand_str = kwarg.get('brand')
        if brand_str:
            brand = self._brand_factory(name=brand_str)
            items_being_updated.append('brand')

            product.brand = brand

        self._record_event(StoreProductUpdatedEvent(
            product_id=product.product_id,
            updated_keys=items_being_updated
        ))

    def update_catalog(self, catalog_id: StoreCatalogId, **kwargs):
        try:
            catalog = next(c for c in self._catalogs if c.catalog_id == catalog_id)

            if 'title' in kwargs.keys():
                catalog.title = kwargs.get('title')

            if 'disabled' in kwargs.keys():
                catalog.disabled = kwargs.get('disabled')

            if 'image' in kwargs.keys():
                catalog.image = kwargs.get('image')
        except StopIteration:
            raise ThingGoneInBlackHoleError(ExceptionMessages.STORE_CATALOG_NOT_FOUND)
        except Exception as exc:
            raise exc
