#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Any, List, Optional, Set, Union

from foundation import EventMixin, ThingGoneInBlackHoleError, new_event_id
from foundation.value_objects.address import Address
from foundation.value_objects.factories import get_money
from shop.adapter.id_generators import SHOP_SUPPLIER_ID_PREFIX, generate_shop_catalog_id, generate_shop_collection_id, \
  generate_brand_id, generate_supplier_id, generate_shop_address_id
from shop.domain.entities.setting import Setting
from shop.domain.entities.shop_address import ShopAddress
from shop.domain.entities.shop_catalog import ShopCatalog
from shop.domain.entities.shop_collection import ShopCollection
from shop.domain.entities.shop_product import ShopProduct
from shop.domain.entities.shop_product_brand import ShopProductBrand
from shop.domain.entities.shop_product_tag import ShopProductTag
from shop.domain.entities.shop_supplier import ShopSupplier, SupplierContact
from shop.domain.entities.shop_user import ShopUser, SystemUser
from shop.domain.entities.shop_warehouse import ShopWarehouse
from shop.domain.entities.value_objects import (
  AddressType,
  ExceptionMessages,
  ShopAddressId,
  ShopCatalogId,
  ShopId,
  ShopStatus,
  ShopSupplierId,
  ShopUserType, GenericShopItemStatus, SystemUserId,
)
from shop.domain.events import ShopCreatedEvent, ShopProductCreatedEvent, ShopProductUpdatedEvent, ShopUserCreatedEvent


class Shop(EventMixin):
  def __init__(
      self,
      shop_id: ShopId,
      name: str,
      first_user: ShopUser,
      status: ShopStatus = ShopStatus.WAREHOUSE_YET_CREATED,
      version: int = 0,
      settings: List[Setting] = None
  ) -> None:
    super(Shop, self).__init__()
    self.shop_id = shop_id
    self.name = name
    self.status = status
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
        # this is only the back up case, should never happens
        shop_admin = ShopUser(
          user_id=first_user.user_id,
          email=first_user.email,
          mobile=first_user.mobile,
          shop_role=ShopUserType.ADMIN
        )

    if shop_admin:
      self._users.add(shop_admin)
      self._admin = shop_admin
    else:
      raise Exception(ExceptionMessages.FAILED_TO_CREATE_SHOP_NO_OWNER)

    # create default catalog
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
                                    first_user: ShopUser) -> "Shop":
    # create the store from registration data
    shop = Shop(
      shop_id=shop_id,
      name=shop_name,
      first_user=first_user
    )

    # raise event
    shop._record_event(
      ShopCreatedEvent(
        event_id=new_event_id(),
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
    shop_product = None  # type:ShopProduct

    # extract product_id from parameters
    product_id = kwargs.get('product_id', None)

    try:
      if product_id:
        shop_product = next(p for p in self._products
                            if p.product_id.lower() == product_id.lower() or p.sku.lower() == sku.lower()
                            and p.status != GenericShopItemStatus.DELETED)
      else:
        shop_product = next(p for p in self._products
                            if p.sku.lower() == sku.lower()
                            and p.status != GenericShopItemStatus.DELETED)

      if shop_product and shop_product.status in [GenericShopItemStatus.NORMAL,
                                                  GenericShopItemStatus.DISABLED]:
        raise Exception(ExceptionMessages.SHOP_PRODUCT_EXISTED)
    except StopIteration:
      pass

    # create PENDING product, a placeholder product to get the ProductId first
    # if kwargs.get('pending', None) is True:
    #     # TODO: Check for the current user who is calling this creating product, see if he has any product that
    #     #  being PENDING or not. If there is his pending product, then return
    #     product = ShopProduct.create_product(
    #         title=title,
    #         sku=sku,
    #         default_unit=default_unit,
    #         status=GenericShopItemStatus.PENDING_CREATION
    #     )
    #
    #     # add to catalog
    #     self._append_product(product)
    #
    #     # return the pending product and end the creation of product here
    #     return product

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
    catalog = None
    catalog_id_str = kwargs.get('catalog_id')
    if catalog_id_str:
      try:
        catalog = next(c for c in self._catalogs if c.catalog_id == catalog_id_str)
      except StopIteration:
        catalog_str = kwargs.get('catalog')
        if catalog_str:
          catalog = self._make_catalog(title=catalog_str)

    if not catalog:
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

    status = GenericShopItemStatus.NORMAL
    if kwargs.get('pending', None) is True:
      status = GenericShopItemStatus.PENDING_CREATION

    # make product
    if shop_product is None:
      shop_product = ShopProduct.create_product(
        title=title,
        sku=sku,
        image=image,
        default_unit=default_unit,
        restock_threshold=restock_threshold,
        max_stock_threshold=max_stock_threshold,
        shop=self,
        brand=brand,
        catalog=catalog,
        collections=collections,
        suppliers=suppliers,
        tags=tags,
        status=status
      )
    else:
      shop_product.title = title
      shop_product.sku = sku
      shop_product.image = image
      shop_product.default_unit = default_unit
      shop_product.restock_threshold = restock_threshold
      shop_product.max_stock_threshold = max_stock_threshold
      shop_product.brand = brand
      shop_product.catalog = catalog
      shop_product.collections = collections
      shop_product.suppliers = suppliers
      shop_product.tags = tags
      shop_product.status = status

    # process input data: StoreProductUnit (which are unit conversions)
    unit_conversions = kwargs.get('unit_conversions', None) or []
    for unit_conversion in unit_conversions:
      shop_product.create_unit(unit_name=unit_conversion['unit'],
                               conversion_factor=unit_conversion['conversion_factor'],
                               base_unit=unit_conversion['base_unit'])

    # process input data: PurchasePrices
    default_currency = self.get_setting('default_currency', 'VND')
    for price in purchase_price_list:
      shop_product.create_purchase_price_by_supplier(
        supplier=self._supplier_factory(supplier_name=price['supplier_name']),
        unit=shop_product.get_unit(price['unit']),
        price=get_money(amount=price['price'],
                        currency_str=price['currency'] if 'currency' in price.keys() and price[
                          'currency'] is not None else default_currency),
        tax=price['tax'],
        effective_from=price['effective_from'],
      )

    # add to catalog
    self._append_product(shop_product)

    # build the array of stocking quantity
    units = [u.unit_name for u in shop_product.units]
    first_stockings_input = kwargs.get('first_inventory_stocking_for_unit_conversions', None) or []
    first_stockings_input = {item['unit']: item['stocking'] for item in first_stockings_input}

    # raise event
    if shop_product.status == GenericShopItemStatus.NORMAL:
      self._record_event(ShopProductCreatedEvent, **dict(
        event_id=new_event_id(),
        shop_id=self.shop_id,
        product_id=shop_product.product_id,
        default_unit=shop_product.default_unit.unit_name,
        units=units,
        first_stocks=[first_stockings_input.get(u, 0) for u in units]
      ))

    return shop_product

  def _append_product(self, product: ShopProduct):
    self._products.add(product)

  # endregion

  def create_brand(self, name: str, logo: Optional[str] = '') -> ShopProductBrand:
    """
    Create or return an existing brand base on its name.
    Update new logo if logo is input and the existing brand not yet have any logo.

    :param name: name of the brand
    :param logo: new logo

    :return: instance of ShopProductBrand
    """
    brand = self._brand_factory(name=name)
    if logo is not None and not brand.logo:
      brand.logo = logo

    return brand

  def _brand_factory(self, name: str) -> ShopProductBrand:
    try:
      brand = next(b for b in self._brands if b.name.lower() == name.lower())
      return brand
    except StopIteration:
      brand = ShopProductBrand(name=name)
      brand.brand_id = generate_brand_id()
      self._brands.add(brand)
      return brand

  def create_supplier(self, supplier_name: str, contact_name: str, contact_phone: str) -> ShopSupplier:
    """
    Create or return an existing supplier base on its name.lower()
    Add or update contact_name and contact_phone

    :param supplier_name: name of the supplier
    :param contact_name: contact's name
    :param contact_phone: contact's phone

    :return: instance of ShopSupplier
    """
    supplier = self._supplier_factory(supplier_name=supplier_name,
                                      contact_name=contact_name,
                                      contact_phone=contact_phone)
    return supplier

  def _supplier_factory(self, supplier_name: str, contact_name: str = None, contact_phone: str = None):
    try:
      # contact = SupplierContact(contact_name=contact_name, contact_phone=contact_phone)
      supplier = next(s for s in self._suppliers if s.supplier_name.lower() == supplier_name.lower())
      # if contact not in supplier.contacts:
      #     supplier.contacts.add(contact)
    except StopIteration:
      # contact = SupplierContact(contact_name=contact_name, contact_phone=contact_phone)
      supplier = ShopSupplier(supplier_name=supplier_name)
      supplier.supplier_id = generate_supplier_id()
      # , contacts=set([contact]))
      self._suppliers.add(supplier)

    contact = SupplierContact(contact_name=contact_name, contact_phone=contact_phone,
                              status=GenericShopItemStatus.NORMAL)
    if contact not in supplier.contacts:
      supplier.contacts.add(contact)

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
      collection.collection_id = generate_shop_collection_id()
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

  def create_default_catalog(self) -> ShopCatalog:
    return self._create_default_catalog()

  def turn_on_default_catalog(self, catalog_id: ShopCatalogId) -> bool:
    try:
      catalog = next(c for c in self.catalogs if c.catalog_id == catalog_id)
      catalog.default = True
      return True
    except StopIteration:
      return False

  def is_catalog_exists(self, catalog_title: str) -> bool:
    catalog_title = catalog_title.strip()
    try:
      c = next(c for c in self._catalogs if c.title.lower() == catalog_title.lower())
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

  def add_address(self, recipient: str, phone: str, address: Address):
    try:
      shop_address = ShopAddress(
        recipient=recipient,
        phone=phone,
        address_type=AddressType.SHOP_ADDRESS,
        address=address,
      )

      if shop_address not in self._addresses:
        shop_address.shop_address_id = generate_shop_address_id()
        self._addresses.add(shop_address)

      return shop_address
    except Exception as exc:
      raise exc

  def get_address(self, address_id: ShopAddressId):
    try:
      address = next(a for a in self._addresses if a.shop_address_id == address_id)
      return address
    except StopIteration:
      return None

  def get_supplier(self, supplier_id_or_name: Union[ShopSupplierId, str]) -> Optional[ShopSupplier]:
    """
    Return an instance of ShopSupplier specified by its id and which is a child of this shop. If no children with this id found, then return None

    :param supplier_id_or_name: Id or Name of the supplier

    :return: an instance of ShopSupplier, or None
    """
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

    self._record_event(ShopProductUpdatedEvent, **dict(
      event_id=new_event_id(),
      shop_id=self.shop_id,
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
      raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_CATALOG_NOT_FOUND)
    except Exception as exc:
      raise exc

  def delete_shop_catalog(self, catalog_id: ShopCatalogId, remove_completely: bool = False):
    try:
      catalog = next(c for c in self._catalogs if c.catalog_id == catalog_id)
      self._catalogs.remove(catalog)

      return catalog
    except StopIteration:
      raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_CATALOG_NOT_FOUND)
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

  def create_user_from_system_user(self, system_user_id: SystemUserId):
    try:
      shop_user = ShopUser(user_id=system_user_id, shop_role=ShopUserType.MANAGER)
      try:
        shop_user = next(u for u in self._users if u.user_id == system_user_id)
      except StopIteration:
        self._users.add(shop_user)

        self._record_event(ShopUserCreatedEvent(
          event_id=new_event_id(),
          shop_id=self.shop_id,
          user_id=shop_user.user_id,
        ))

      return shop_user
    except Exception as exc:
      raise exc
