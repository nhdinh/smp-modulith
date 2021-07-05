#!/usr/bin/env python
# -*- coding: utf-8 -*-
import uuid
from typing import Set, List, Union, TYPE_CHECKING, Any, Optional, NewType
from uuid import UUID

from foundation.common_helpers import slugify
from foundation.events import EventMixin
from foundation.value_objects.address import LocationAddress
from foundation.value_objects.factories import get_money
from store.application.usecases.const import ExceptionMessages
from store.domain.entities.setting import Setting
from store.domain.entities.store_address import StoreAddress, StoreAddressType, StoreAddressId
from store.domain.entities.store_catalog import StoreCatalog, StoreCatalogId, StoreCatalogReference
from store.domain.entities.store_collection import StoreCollection, StoreCollectionReference
from store.domain.entities.store_owner import StoreOwner
from store.domain.entities.store_product import StoreProduct, StoreProductReference
from store.domain.entities.store_product_brand import StoreProductBrand
from store.domain.entities.store_product_tag import StoreProductTag
from store.domain.entities.store_supplier import StoreSupplier, StoreSupplierId
from store.domain.entities.store_warehouse import StoreWarehouse
from store.domain.events.store_created_event import StoreCreatedEvent
from store.domain.events.store_product_created_event import StoreProductCreatedEvent

StoreId = NewType('StoreId', tp=UUID)
StoreCatalogIdOrReference = Union[StoreCatalogId, StoreCatalogReference]


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

        # reference string
        reference = slugify(title)
        reference_str = kwargs.get('reference')
        if reference_str:
            reference = slugify(reference_str)

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
            catalog = self._catalog_factory(title=catalog_str)
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
            reference=reference,
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
            store_id=self.store_id,
            product_id=store_product.product_id,
            default_unit=store_product.default_unit.unit_name,
            units=units,
            first_stocks=[first_stockings_input.get(u, 0) for u in units]
        ))

        return store_product

    def _append_product(self, product: StoreProduct):
        if self._is_product_reference_exists(product.reference):
            product.reference = self._generate_new_product_reference(base_on=product.reference)

        self._products.add(product)

    def _is_product_reference_exists(self, product_reference: StoreProductReference):
        try:
            product = next(p for p in self._products if p.reference == product_reference)
            if product:
                return True
        except StopIteration:
            return False
        else:
            return False

    def _generate_new_product_reference(self, base_on: str) -> str:
        return self.__generate_new_reference(base_on)

    # endregion

    @staticmethod
    def __generate_new_reference(base_on: str) -> str:
        return base_on + '_' + uuid.uuid4().hex.upper()[0:6]

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

    def _is_collection_reference_exists(self, collection_reference: StoreCollectionReference,
                                        parent_catalog: StoreCatalog):
        try:
            collection = next(
                c for c in self._collections if c.reference == collection_reference and c.catalog == parent_catalog)
            if collection:
                return True
        except StopIteration:
            return False

    def _generate_new_collection_reference(self, base_on: str) -> str:
        return self.__generate_new_reference(base_on=base_on)

    def _collection_factory(self, title: str, parent_catalog: StoreCatalog) -> StoreCollection:
        try:
            collection = next(coll for coll in self._collections if
                              coll.title.lower() == title.strip().lower() and coll.catalog == parent_catalog)
            return collection
        except StopIteration:
            collection = self._create_collection(title=title, parent_catalog=parent_catalog)
            self._collections.add(collection)
            return collection

    def _create_collection(self, title: str, parent_catalog: StoreCatalog, **kwargs) -> StoreCollection:
        reference_str = kwargs.get('reference')
        if reference_str:
            reference = slugify(reference_str)
        else:
            reference = slugify(title)

        is_default = kwargs.get('default')
        if is_default is None:
            is_default = False

        if self._is_collection_reference_exists(collection_reference=reference, parent_catalog=parent_catalog):
            reference = self._generate_new_collection_reference(base_on=reference)

        # make collection
        collection = StoreCollection(reference=reference, title=title, default=is_default)
        collection._catalog = parent_catalog

        return collection

    def _catalog_factory(self, title: str) -> StoreCatalog:
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
        reference_str = kwargs.get('reference')
        if reference_str:
            reference = slugify(reference_str)
        else:
            reference = slugify(title)

        is_default = kwargs.get('default')
        if is_default is None:
            is_default = False

        if self.is_catalog_reference_exists(catalog_reference=reference):
            reference = self._generate_new_catalog_reference(base_on=reference)

        # make catalog
        catalog = StoreCatalog(reference=reference, title=title, default=is_default)

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

    def turn_on_default_catalog(self, catalog_reference: StoreCatalogReference) -> bool:
        try:
            catalog = next(c for c in self.catalogs if c.reference == catalog_reference)
            catalog.default = True
            return True
        except StopIteration:
            return False

    def _generate_new_catalog_reference(self, base_on: str) -> str:
        """
        Generate a new unique catalog reference base on the input string

        :param base_on: string (prefix) of the reference
        :return: str
        """
        return self.__generate_new_reference(base_on)

    def is_catalog_reference_exists(self, catalog_reference: str) -> bool:
        try:
            c = next(c for c in self._catalogs if c.reference == catalog_reference)
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
            warehouse_id=uuid.uuid4(),
            store_id=self.store_id,
            warehouse_owner=self.owner_email,
            warehouse_name=warehouse_name,
            default=False,
            disabled=False
        )

    def contains_catalog_reference(self, catalog_reference: StoreCatalogReference):
        try:
            catalog = next(c for c in self.catalogs if c.reference == catalog_reference)
            if catalog:
                return True
        except StopIteration:
            return False

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
            if isinstance(supplier_id_or_name, UUID):
                supplier = next(s for s in self._suppliers if s.supplier_id == supplier_id_or_name)
                return supplier
            elif isinstance(supplier_id_or_name, str):
                supplier = next(s for s in self._suppliers if s.supplier_name == supplier_id_or_name)
                return supplier
            else:
                raise TypeError
        except StopIteration:
            return None
