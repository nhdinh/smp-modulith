#!/usr/bin/env python
# -*- coding: utf-8 -*-
import uuid
from datetime import datetime
from typing import Set, List, Union, Any, Optional

from foundation.domain_events.shop_events import ShopCreatedEvent, ShopProductUpdatedEvent
from foundation.events import EventMixin, ThingGoneInBlackHoleError
from foundation.value_objects.address import LocationAddress
from foundation.value_objects.factories import get_money
from shop.adapter.id_generators import generate_shop_catalog_id, SHOP_SUPPLIER_ID_PREFIX
from shop.domain.entities.setting import Setting
from shop.domain.entities.shop_address import ShopAddress
from shop.domain.entities.shop_catalog import ShopCatalog
from shop.domain.entities.shop_supplier import ShopSupplier
from shop.domain.entities.shop_user import ShopUser, SystemUser
from shop.domain.entities.store_collection import ShopCollection
from shop.domain.entities.store_product import ShopProduct
from shop.domain.entities.store_product_brand import ShopProductBrand
from shop.domain.entities.store_product_tag import ShopProductTag
from shop.domain.entities.store_warehouse import ShopWarehouse
from shop.domain.entities.value_objects import ShopId, ShopUserType, ExceptionMessages, ShopCatalogId, StoreAddressId, \
    StoreSupplierId, AddressType


class Shop(EventMixin):
    def __init__(self, shop_id: ShopId, name: str, first_user: Union[SystemUser, ShopUser], version: int = 0,
                 settings: List[Setting] = None) -> None:
        super(Shop, self).__init__()

        self.shop_id = shop_id
        self.name = name
        self.version = version

        if settings:
            self._settings = settings
        else:
            self._settings = self._default_settings

        self._users = set()  # type: Set[ShopUser]
        self._admin = None

        shop_admin = None
        if first_user is not None:
            if isinstance(first_user, ShopUser):
                shop_admin = first_user
                shop_admin.shop_role = ShopUserType.ADMIN
            elif isinstance(first_user, SystemUser):
                shop_admin = ShopUser(_system_user=first_user, shop_role=ShopUserType.ADMIN)

        if shop_admin:
            self._users.add(shop_admin)
            self._admin = shop_admin
        else:
            raise Exception(ExceptionMessages.FAILED_TO_CREATE_STORE_NO_OWNER)

        # create default catalot
        self._catalogs = set()  # type: Set[ShopCatalog]
        default_catalog = self._create_default_catalog()
        self._catalogs.add(default_catalog)

        # children data
        self._addresses = set()  # type:Set[ShopAddress]
        self._warehouses = set()  # type: Set[ShopWarehouse]
        self._brands = set()  # type: Set[ShopProductBrand]
        self._suppliers = set()  # type:Set[ShopSupplier]
        self._collections = set()  # type: Set[ShopCollection]
        self._products = set()  # type: Set[ShopProduct]

    # region ## Properties ##
    @property
    def users(self) -> Set[ShopUser]:
        return self._users

    @property
    def shop_admin(self) -> ShopUser:
        return self._admin

    @property
    def settings(self) -> Set[Setting]:
        return set() if self._settings is None else self._settings

    @property
    def warehouses(self) -> Set[ShopWarehouse]:
        return self._warehouses

    @property
    def addresses(self) -> Set[ShopAddress]:
        return self._addresses

    @property
    def catalogs(self) -> Set[ShopCatalog]:
        return self._catalogs

    @property
    def products(self) -> Set[ShopProduct]:
        return self._products

    @property
    def suppliers(self) -> Set[ShopSupplier]:
        return self._suppliers

    @property
    def default_warehouse(self) -> Optional[ShopWarehouse]:
        try:
            default_warehouse = next(w for w in self._warehouses if w.default)
            return default_warehouse
        except StopIteration:
            return None

    @property
    def brands(self) -> Set[ShopProductBrand]:
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
        _settings.add(Setting('default_catalog_display_name', 'Chưa phân loại', 'str'))
        _settings.add(Setting('default_collection_display_name', 'Chưa phân loại', 'str'))
        _settings.add(Setting('default_currency', 'VND', 'str'))

        return _settings

    # endregion

    # region ## Creating new store ##
    @classmethod
    def create_shop_from_registration(cls, shop_id: ShopId, shop_name: str,
                                      first_user: Union[SystemUser, ShopUser]) -> "Shop":
        # create the store from registration data
        shop = Shop(
            shop_id=shop_id,
            name=shop_name,
            first_user=first_user
        )

        # raise event
        shop._record_event(ShopCreatedEvent(event_id=uuid.uuid4(),
                                            shop_id=shop.shop_id,
                                            shop_name=shop.name,
                                            admin_email=shop.shop_admin.email,
                                            admin_id=shop.shop_admin.user_id,
                                            shop_created_at=datetime.now(),
                                            ))

        return shop

    # endregion

    # region ## Products Management ##
    def create_product(self,
                       title: str,
                       sku: str,
                       default_unit: str,
                       **kwargs) -> ShopProduct:
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
        store_product = ShopProduct.create_product(
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

    def _append_product(self, product: ShopProduct):
        self._products.add(product)

    # endregion

    def _brand_factory(self, name: str) -> ShopProductBrand:
        try:
            brand = next(b for b in self._brands if b.name.lower() == name.strip().lower())
            return brand
        except StopIteration:
            brand = ShopProductBrand(name=name)
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
            supplier = ShopSupplier(supplier_name=supplier_name,
                                    contact_name=contact_name,
                                    contact_phone=contact_phone)
            # , contacts=set([contact]))
            self._suppliers.add(supplier)
            return supplier

    def _is_collection_exists(self, title: str, parent_catalog: ShopCatalog):
        try:
            collection = next(
                c for c in self._collections if c.title == title and c.catalog == parent_catalog)
            if collection:
                return True
        except StopIteration:
            return False

    def _collection_factory(self, title: str, parent_catalog: ShopCatalog) -> ShopCollection:
        try:
            collection = next(coll for coll in self._collections if
                              coll.title.lower() == title.strip().lower() and coll.catalog == parent_catalog)
            return collection
        except StopIteration:
            collection = self.make_collection(title=title, parent_catalog=parent_catalog)
            self._collections.add(collection)
            return collection

    def make_collection(self, title: str, parent_catalog: ShopCatalog, **kwargs) -> ShopCollection:
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

            collection = ShopCollection(title=title, default=is_default)
            parent_catalog.collections.add(collection)
            self._collections.add(collection)

            return collection

    def _make_catalog(self, title: str) -> ShopCatalog:
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

    def create_catalog(self, title: str, **kwargs) -> ShopCatalog:
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
        catalog = ShopCatalog(title=title, default=is_default)
        catalog.catalog_id = generate_shop_catalog_id()

        # make default collection

        return catalog

    def _create_default_catalog(self) -> ShopCatalog:
        """
        Create a default `StoreCatalog` instance

        :return: an instance of the `StoreCatalog`
        """
        catalog_title = self.get_setting('default_catalog_title', 'Catalog')
        is_default = True

        return self.create_catalog(title=catalog_title, default=is_default)

    def turn_on_default_catalog(self, catalog_id: ShopCatalogId) -> bool:
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

    def append_tags_stack(self, tags: List[ShopProductTag]):
        pass

    # region ## Internal class method ##
    def __str__(self) -> str:
        return f'<{self.__class__.__name__} #{self.shop_id} name="{self.name}" >'

    def __eq__(self, other) -> bool:
        return isinstance(other, Shop) and self.shop_id == other.shop_id

    # endregion
    def create_warehouse(self, warehouse_name: str):
        raise NotImplementedError
        # if len(self._warehouses) >= 1:
        #     raise Exception('Sorry. This version of application only allow to create 01 warehouse per store.')
        #
        # """
        # Create a new warehouse for this store
        #
        # :param warehouse_name: name of the warehouse
        # :return: instance of the warehouse
        # """
        # return ShopWarehouse(
        #     warehouse_id=generate_warehouse_id(),
        #     store_id=self.shop_id,
        #     warehouse_owner=self.owner_email,
        #     warehouse_name=warehouse_name,
        #     default=False,
        #     disabled=False
        # )

    # def contains_catalog_reference(self, catalog_reference: StoreCatalogReference):
    #     try:
    #         catalog = next(c for c in self.catalogs if c.reference == catalog_reference)
    #         if catalog:
    #             return True
    #     except StopIteration:
    #         return False

    def add_address(self, recipient: str, phone: str, address: LocationAddress):
        try:
            store_address = ShopAddress(
                recipient=recipient,
                phone=phone,
                address_type=AddressType.SHOP_ADDRESS,
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
            address = next(a for a in self._addresses if a.shop_address_id == address_id)
            return address
        except StopIteration:
            return None

    def get_supplier(self, supplier_id_or_name: Union[StoreSupplierId, str]):
        try:
            if isinstance(supplier_id_or_name, str) and supplier_id_or_name.startswith(SHOP_SUPPLIER_ID_PREFIX):
                supplier = next(s for s in self._suppliers if s.supplier_id == supplier_id_or_name)
                return supplier
            elif isinstance(supplier_id_or_name, str):
                supplier = next(s for s in self._suppliers if s.supplier_name == supplier_id_or_name)
                return supplier
            else:
                raise TypeError
        except StopIteration:
            return None

    def update_product(self, product: ShopProduct, **kwarg):
        items_being_updated = []

        brand_str = kwarg.get('brand')
        if brand_str:
            brand = self._brand_factory(name=brand_str)
            items_being_updated.append('brand')

            product.brand = brand

        collections_str_list = kwarg.get('collections')
        if collections_str_list:
            for collection_str in collections_str_list:
                collection = self._collection_factory(title=collection_str, parent_catalog=product.catalog)
                if collection not in product.collections:
                    product.collections.add(collection)
                    items_being_updated.append('collections')

        self._record_event(ShopProductUpdatedEvent(
            product_id=product.product_id,
            updated_keys=items_being_updated
        ))

    def update_catalog(self, catalog_id: ShopCatalogId, **kwargs):
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

    def delete_shop_catalog(self, catalog_id: ShopCatalogId, remove_completely: bool = False):
        try:
            catalog = next(c for c in self._catalogs if c.catalog_id == catalog_id)
            self._catalogs.remove(catalog)

            return catalog
        except StopIteration:
            raise ThingGoneInBlackHoleError(ExceptionMessages.STORE_CATALOG_NOT_FOUND)
        except Exception as exc:
            raise exc

    def add_warehouse(self, warehouse_id: 'WarehouseId', warehouse_name: str):
        try:
            warehouse = next(w for w in self._warehouses if w.warehouse_id == warehouse_id)
            return warehouse
        except StopIteration:
            warehouse = ShopWarehouse(warehouse_id=warehouse_id, shop_id=self.shop_id, warehouse_name=warehouse_name)
            self._warehouses.add(warehouse)
            return warehouse
