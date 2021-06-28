#!/usr/bin/env python
# -*- coding: utf-8 -*-
import uuid
from typing import Set, List, Union, TYPE_CHECKING, Any

from foundation import slugify
from foundation.events import EventMixin
from store.application.usecases.const import ExceptionMessages
from store.domain.entities.setting import Setting
from store.domain.entities.store_catalog import StoreCatalog
from store.domain.entities.store_collection import StoreCollection
from store.domain.entities.store_owner import StoreOwner
from store.domain.entities.store_product import StoreProduct
from store.domain.entities.store_product_brand import StoreProductBrand
from store.domain.entities.store_product_tag import StoreProductTag
from store.domain.entities.value_objects import StoreId, StoreCatalogReference, StoreCatalogId, \
    StoreCollectionReference, StoreProductReference
from store.domain.events.store_created_event import StoreCreatedEvent

if TYPE_CHECKING:
    pass

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
        self._brands = set()  # type: Set[StoreProductBrand]
        self._catalogs = set()  # type: Set
        self._collections = set()  # type: Set
        self._products = set()  # type: Set[StoreProduct]

    # region ## Properties ##
    @property
    def catalogs(self) -> Set[StoreCatalog]:
        return self._catalogs

    @property
    def products(self) -> Set[StoreProduct]:
        return self._products

    @property
    def brands(self) -> Set[StoreProductBrand]:
        return self._brands

    @property
    def settings(self) -> Set[Setting]:
        return set() if self._settings is None else self._settings

    def _get_setting(self, key: str, default_value: Any = None):
        try:
            setting = next(s for s in self._settings if s.key == key)
            return setting.value
        except StopIteration:
            return default_value

    @property
    def _default_settings(self) -> Set[Setting]:
        _settings = set()  # type: Set[Setting]
        _settings.add(Setting('default_page_size', '10', 'int'))
        _settings.add(Setting('default_catalog_reference', 'unassigned_catalog', 'str'))
        _settings.add(Setting('default_catalog_display_name', 'Chưa phân loại', 'str'))
        _settings.add(Setting('default_collection_reference', 'unassigned_collection', 'str'))
        _settings.add(Setting('default_collection_display_name', 'Chưa phân loại', 'str'))

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
        restock_threshold, maxstock_threshold = 0, 0
        restock_thrh_str = kwargs.get('restock_threshold')
        maxstock_thrh_str = kwargs.get('maxstock_threshold')
        try:
            restock_threshold = int(restock_thrh_str)
        except:
            restock_threshold = -1

        try:
            maxstock_threshold = int(maxstock_thrh_str)
        except:
            maxstock_threshold = -1

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
            maxstock_threshold=maxstock_threshold,
            store=self,
            brand=brand,
            catalog=catalog,
            collections=collections,
            tags=tags
        )

        # process input data: StoreProductUnit (which are unit conversions)
        unit_conversions = kwargs.get('unit_conversions')
        for unit_conversion in unit_conversions:
            store_product.create_unit(unit_name=unit_conversion['unit'],
                                      conversion_factor=unit_conversion['conversion_factor'],
                                      base_unit=unit_conversion['base_unit'])

        # add to catalog
        self._append_product(store_product)

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
        catalog_reference = self._get_setting('default_catalog_reference', 'unassigned_catalog')
        catalog_title = self._get_setting('default_catalog_title', 'Catalog')
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
