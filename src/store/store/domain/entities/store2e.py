#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from typing import Set, List, Any, Optional, Union, Dict, TYPE_CHECKING

from foundation import slugify, uuid_validate
from foundation.entity import Entity
from foundation.events import EventMixin
from store.application.usecases.const import ExceptionMessages
from store.domain.entities.setting import Setting
from store.domain.entities.store_catalog import StoreCatalog
from store.domain.entities.store_collection import StoreCollection
from store.domain.entities.store_owner import StoreOwner
from store.domain.entities.store_product import StoreProduct
from store.domain.entities.store_product_brand import StoreProductBrand, StoreProductBrandReference
from store.domain.entities.store_product_tag import StoreProductTag
from store.domain.entities.store_unit import StoreProductUnit
from store.domain.entities.value_objects import StoreId, StoreCatalogReference, StoreCollectionReference, \
    StoreCatalogId, StoreProductReference
from store.domain.events.store_catalog_events import StoreCatalogUpdatedEvent, StoreCatalogToggledEvent, \
    StoreCatalogCreatedEvent, StoreCollectionCreatedEvent, StoreCatalogDeletedEvent, StoreCollectionToggledEvent, \
    StoreCollectionUpdatedEvent, StoreCollectionDeletedEvent
from store.domain.events.store_created_event import StoreCreatedEvent
from store.domain.rules.default_passed_rule import DefaultPassedRule

if TYPE_CHECKING:
    from store.application.usecases.product.create_store_product_uc import CreatingStoreProductUnitConversionRequest



class Stor2e(EventMixin, Entity):
    store_id: StoreId
    name: str
    disabled: bool

    def __init__(
            self,
            store_id: StoreId,
            store_name: str,
            store_owner: StoreOwner,
            version: int = 0,
            settings: List[Setting] = None
    ):
        super(Store, self).__init__()

        # check rules
        self.check_rule(DefaultPassedRule())

        self.store_id = store_id
        self.name = store_name
        self.disabled = False

        # make a list of StoreOwner and Manager
        self._owner = store_owner
        self._managers = set()

        # initial settings
        if settings and type(settings) is List:
            self._settings = set(settings)
        else:
            self._settings: Set[Setting] = Store.default_settings()

        # raise the event
        self._raise_store_created_event()

        # build cache
        self._cached = {
            'catalogs': [],
            'collections': [],
            'products': []
        }

        # its catalog
        self._catalogs = set()  # type:Set[StoreCatalog]
        default_catalog = self._create_system_catalog()
        self._add_catalog_to_store(catalog=default_catalog)

        # its brands
        self._brands = set()  # type:Set[StoreProductBrand]

        # version number
        self.version = version

    # region ## Properties ##

    @property
    def owner_email(self) -> str:
        return getattr(self, 'owner_email')

    @property
    def settings(self) -> dict:
        """
        Contains a set of `Setting` that applied to this store

        :return: set of `Setting` data
        """
        return {setting.key: setting.get_value() for setting in self._settings}

    @property
    def owner(self) -> StoreOwner:
        """
        Return an `User` that is owner of this store

        :return: instance of `User`
        """
        return self._owner

    @property
    def managers(self) -> Set:
        """
        Return a list of `User` that are managers of this Store

        :return: set of `User` instances
        """
        return self._managers

    @property
    def catalogs(self) -> Set[StoreCatalog]:
        """
        Return a list of children `StoreCatalog`

        :return:
        """
        return self._catalogs

    @property
    def brands(self) -> Set[StoreProductBrand]:
        return self._brands

    @property
    def system_catalog(self) -> Optional[StoreCatalog]:
        if not hasattr(self, '_catalogs'):
            return None

        try:
            catalog = next(c for c in self._catalogs if c.system)  # type:StoreCatalog
            return catalog
        except StopIteration:
            return None

    # endregion

    @classmethod
    def create_store_from_registration(cls, store_id, store_name, store_owner):
        # create the store from registration data
        store = Store(
            store_id=store_id,
            store_name=store_name,
            store_owner=store_owner
        )

        return store

    # region ## StoreSetting Operations ##

    def update_settings(self, setting_key: str, setting_value: Union[str, int, float]):
        setting = Setting(key=setting_key, value=str(setting_value), type=type(setting_value))
        self._settings.add(setting)

    def has_setting(self, setting_key: str):
        """
        Return the existence of the setting_key in store settlngs selve
        :param setting_key:
        :return:
        """
        return setting_key in self.settings.keys()

    def get_setting(self, setting_key: str, default_value: Any):
        if setting_key == 'default_catalog_reference':
            return 'unassigned_catalog'

        if setting_key == 'default_collection_reference':
            return 'unassigned_collection'

        # else
        if self.has_setting(setting_key):
            return self.settings[setting_key]
        else:
            return default_value

    def remove_setting(self, setting_key: str):
        if self.has_setting(setting_key):
            # setting = self.get_setting(setting_key)
            self.settings.pop(setting_key)

    # endregion

    # region ## StoreCatalog Operations ##

    def contains_catalog_reference(self, catalog_reference: StoreCatalogReference):
        """
        Return the existence of specified `catalog_reference` in this store

        :param catalog_reference: Reference of the catalog to search for
        """

        _cached = self._build_cache()
        return catalog_reference in _cached['catalogs']

    def fetch_catalog_by_id_or_reference(self, search_term: str) -> Optional[StoreCatalog]:
        try:
            catalog = None
            catalog_id = uuid_validate(search_term)
            if catalog_id:
                catalog = self._fetch_catalog_by_id(catalog_id=catalog_id)
            else:
                catalog = self._fetch_catalog_by_reference(catalog_reference=search_term)

            return catalog
        except Exception as exc:
            raise exc

    def _fetch_catalog_by_reference(self, catalog_reference: StoreCatalogReference) -> Optional[StoreCatalog]:
        """
        Get child catalog by catalog_reference

        :param catalog_reference: reference of a catalog to fetch
        :return: instance of `Catalog` or None
        """
        if not hasattr(self, '_catalogs'):
            return None

        try:
            catalog = next(c for c in self._catalogs if c.reference == catalog_reference)  # type:StoreCatalog
            return catalog
        except StopIteration:
            return None

    def _fetch_catalog_by_id(self, catalog_id: StoreCatalogId) -> Optional[StoreCatalog]:
        if not hasattr(self, '_catalogs'):
            return None

        try:
            catalog = next(c for c in self._catalogs if c.catalog_id == catalog_id)
            return catalog
        except StopIteration:
            return None

    def toggle_catalog(self, catalog_reference: StoreCatalogReference) -> None:
        """
        Toggle the catalog on/ off

        :param catalog_reference: reference of the catalogs
        """
        try:
            catalog = self._fetch_catalog_by_reference(catalog_reference=catalog_reference)  # type:StoreCatalog
            if not catalog:
                raise Exception(ExceptionMessages.STORE_CATALOG_NOT_FOUND)

            self._toggle_catalog(catalog)
        except Exception as exc:
            raise exc

    def _toggle_catalog(self, catalog: StoreCatalog) -> None:
        """

        Internal method for toggle catalog

        :param catalog:
        """
        try:
            catalog.toggle()

            self._record_event(StoreCatalogToggledEvent(
                store_id=self.store_id,
                catalog_id=catalog.catalog_id,
                catalog_reference=catalog.reference,
                disabled=catalog.disabled
            ))
        except Exception as exc:
            raise exc

    def update_catalog(self, catalog_reference: StoreCatalogReference, update_data: dict) -> None:
        """
        Update the child catalog with input data

        :param catalog_reference: reference of the catalog
        :param update_data:
        """
        try:
            catalog = self._fetch_catalog_by_reference(catalog_reference=catalog_reference)

            if not catalog:
                raise Exception(ExceptionMessages.STORE_CATALOG_NOT_FOUND)

            # prevent to change status of system catalog
            if catalog.system and 'disabled' in update_data.keys():
                update_data.pop('disabled')

            self._update_catalog(catalog, update_data=update_data)
        except Exception as exc:
            raise exc

    def _update_catalog(self, catalog: StoreCatalog, update_data: Dict) -> None:
        try:
            for key, value in update_data.items():
                setattr(catalog, key, value)

            self._record_event(StoreCatalogUpdatedEvent(
                store_id=self.store_id,
                catalog_id=catalog.catalog_id,
                catalog_reference=catalog.reference
            ))
        except Exception as exc:
            raise exc

    def create_store_catalog(self, display_name: str, **kwargs):
        try:
            input_reference = kwargs.get('reference')
            reference = slugify(input_reference) if input_reference else slugify(display_name)

            disabled = kwargs.get('disabled', None)
            if disabled is None:
                disabled = False

            system = kwargs.get('system', None)
            if system is None:
                system = False

            display_image = kwargs.get('display_image')

            # check input_reference
            # if user specified the catalog reference with input_reference, then need to check if the reference has been taken or not. Raise if taken
            if input_reference:
                reference_has_been_taken = self.contains_catalog_reference(catalog_reference=reference)
                if reference_has_been_taken:
                    raise Exception(ExceptionMessages.STORE_CATALOG_EXISTED)
            else:
                if self.contains_catalog_reference(catalog_reference=reference):
                    # make a new catalog_reference
                    reference = self._make_new_catalog_reference(reference=reference)

            catalog = StoreCatalog.create_instance(
                display_name=display_name,
                reference=reference,
                display_image=display_image,
                disabled=disabled,
                system=system
            )

            # add the new catalog to this store
            self._add_catalog_to_store(catalog=catalog, check_duplicated_reference=False)

            # create the default collection
            default_collection_reference = self.get_setting('default_collection_reference', 'unassigned_collection')
            default_collection_display_name = self.get_setting('default_collection_display_name', 'Default Collection')
            collection = self._create_store_collection(display_name=default_collection_display_name,
                                                       reference=default_collection_reference, default=True)

            if catalog.has_collection_reference(reference=collection.reference):
                collection.reference = catalog.next_collection_reference(base_reference=collection.reference)

            self._add_collection_to_catalog(collection=collection, dest=catalog)

            return catalog
        except Exception as exc:
            raise exc

    def _add_catalog_to_store(self, catalog: StoreCatalog, check_duplicated_reference: bool = True):
        """
        Add the `catalog` into self catalogs children

        :param check_duplicated_reference: enable reference duplication checking before added (default is True)
        :param catalog: the catalog to add
        :return: id of the catalog
        """
        if check_duplicated_reference:
            if self.contains_catalog_reference(catalog_reference=catalog.reference):
                raise Exception(ExceptionMessages.STORE_CATALOG_EXISTED)

        # assign store_id to children catalog and collection
        catalog.store = self
        for collection in catalog.collections:
            collection.store = self

        self._catalogs.add(catalog)

        # add catalog event
        self._raise_catalog_created_event(catalog=catalog)

        return catalog.catalog_id

    def _create_system_catalog(self) -> StoreCatalog:
        """
        Make default catalog for store

        :return: instance of `StoreCatalog`
        """
        try:
            default_catalog_reference = self.get_setting('default_catalog_reference', 'default_catalog')
            default_catalog_name = self.get_setting('default_catalog_display_name', 'Default Catalog')

            # create the new StoreCatalog as default catalog
            return self.create_store_catalog(
                reference=default_catalog_reference,
                display_name=default_catalog_name,
                display_image='',
                disabled=False,
                system=True
            )
        except Exception as exc:
            raise exc

    def turn_on_system_catalog(self, catalog_reference: StoreCatalogReference):
        """
        Make the catalog to system catalog

        :param catalog_reference: reference of the catalog
        """
        try:
            catalog = self._fetch_catalog_by_reference(catalog_reference=catalog_reference)  # type:StoreCatalog
            if not catalog:
                raise Exception(ExceptionMessages.STORE_CATALOG_NOT_FOUND)

            self._turn_on_system_catalog(catalog)
        except Exception as exc:
            raise exc

    def _turn_on_system_catalog(self, catalog: StoreCatalog):
        try:
            for _catalog in self.catalogs:
                _catalog.system = False

            # set the one's system to True
            catalog.system = True
            catalog.disabled = False

            # record the event
            self._record_event(StoreCatalogToggledEvent(
                store_id=self.store_id,
                catalog_id=catalog.catalog_id,
                catalog_reference=catalog.reference,
                disabled=catalog.disabled
            ))
        except Exception as exc:
            raise exc

    def _try_get_catalog_or_create(
            self,
            reference: Optional[StoreCatalogReference] = '',
            display_name: Optional[str] = ''
    ) -> StoreCatalog:
        catalog_reference = reference
        catalog_display_name = display_name
        catalog = None

        # if no catalog_reference and no display_name as well, we would return the default catalog
        if not catalog_reference:
            if not catalog_display_name:
                catalog = self.system_catalog
                if catalog:
                    return catalog
            else:
                # but if there is display_name, we would make the reference out of the display_name by slugify it
                catalog_reference = slugify(catalog_display_name)

        # then fetch catalog by the reference
        if catalog_reference:
            catalog_reference = slugify(catalog_reference)
            catalog = self._fetch_catalog_by_reference(catalog_reference=catalog_reference)

        # if catalog found
        if catalog:
            # and if the user input display_name. If the fetched catalog has different display_name, then it's a different one. Then we would generate a new catalog reference for it, set the fetch_catalog to None
            if catalog_display_name and catalog.display_name.lower() != catalog_display_name.lower():
                catalog_reference = self._make_new_catalog_reference(catalog_reference)
                catalog = None
            else:
                return catalog

        # if the catalog is set to None, then we need to create it
        if not catalog:
            catalog_display_name = 'Unnammed' if not catalog_display_name else catalog_display_name
            catalog = self.create_store_catalog(reference=catalog_reference, display_name=catalog_display_name)
            self._add_catalog_to_store(catalog)

        return catalog

    def _try_get_collection_or_create(
            self,
            parent_catalog: StoreCatalog,
            collection_reference: Optional[StoreCollectionReference] = '',
            collection_display_name: Optional[str] = '',
    ) -> StoreCollection:
        collection = None

        if not collection_reference:
            if not collection_display_name:
                collection = parent_catalog.default_collection
                if collection:
                    return collection
            else:
                collection_reference = slugify(collection_display_name)

        if collection_reference:
            collection_reference = slugify(collection_reference)
            collection = parent_catalog.get_collection_by_reference(collection_reference=collection_reference)

        if collection:
            if collection_display_name and collection.display_name.lower() != collection_display_name.lower():
                collection_reference = parent_catalog.next_collection_reference(base_reference=collection_reference)
                collection = None
            else:
                return collection

        if not collection:
            collection_display_name = 'Unnamed' if not collection_display_name else collection_display_name
            collection = self.create_store_collection(reference=collection_reference,
                                                      display_name=collection_display_name)
            self._add_collection_to_catalog(collection=collection, dest=parent_catalog)

        return collection

    def move_catalog_children(self,
                              source_reference: StoreCatalogReference,
                              dest_reference: Optional[StoreCatalogReference] = None) -> None:
        """
        Move content of a catalog to another one

        :param source_reference: Reference of a source catalog

        :param dest_reference: Reference of a destination catalog. Specified as 'default' or leave it None to tell
        the method to move to default catalog
        """
        try:
            source_catalog = self._fetch_catalog_by_reference(catalog_reference=source_reference)

            if not dest_reference or dest_reference == 'default' or dest_reference == '':
                dest_catalog = self.system_catalog
            else:
                dest_catalog = self._fetch_catalog_by_reference(catalog_reference=dest_reference)

            # make sure that the two catalogs is not identical
            if source_catalog == dest_catalog:
                raise Exception(ExceptionMessages.CANNOT_MOVE_CATALOG_CONTENT_TO_ITSELF)

            self._move_catalog_children(source=source_catalog, dest=dest_catalog)
        except Exception as exc:
            raise exc

    def _move_catalog_children(self, source: StoreCatalog, dest: StoreCatalog) -> None:
        try:
            # ok, so move now
            while len(source.collections):
                collection = source.collections.pop()

                # add collection to catalog, with all to be removed as default
                # dest.add_collection(collection, keep_default=False)
                self._add_collection_to_catalog(collection=collection, dest=dest, keep_default=True)

                # raise event
                self._raise_collection_created_event(collection=collection)
        except Exception as exc:
            raise exc

    def delete_store_catalog(self, catalog_reference: StoreCatalogReference, **kwargs, ) -> None:
        """
        Search and delete a catalog by its reference

        :param catalog_reference: reference of a catalog to delete

        :param kwargs: Options

        Options can contains:

        * `delete_completely`: bool value. Specify `True` if need to discard all of catalog's contents. Else,
        specify `False`, then content of the catalog will be move to the default catalog.

        """

        try:
            # find catalog
            if not self.contains_catalog_reference(catalog_reference=catalog_reference):
                raise Exception(ExceptionMessages.STORE_CATALOG_NOT_FOUND)

            # check if the catalog to be deleted is not system
            catalog_to_be_deleted = self._fetch_catalog_by_reference(catalog_reference=catalog_reference)

            # check if catalog_to_deleted is system catalog
            if catalog_to_be_deleted.system:
                raise Exception(ExceptionMessages.SYSTEM_STORE_CATALOG_CANNOT_BE_REMOVED)

            remove_completely = kwargs.get('remove_completely')
            if not remove_completely:  # move the data to default_catalog
                default_catalog = self.system_catalog
                self._move_catalog_children(source=catalog_to_be_deleted, dest=default_catalog)

            self._raise_catalog_delete_event(catalog=catalog_to_be_deleted, delete_completely=remove_completely)

            # delete the specified one
            self._delete_store_catalog(catalog=catalog_to_be_deleted)
        except Exception as exc:
            raise exc

    def _delete_store_catalog(self, catalog: StoreCatalog) -> None:
        """
        Internal delete function (work with entities)

        """
        try:
            self.catalogs.remove(catalog)
            del catalog
            # del catalog
        except Exception as exc:
            raise exc

    def _make_new_catalog_reference(self, reference: StoreCatalogReference) -> str:
        try:
            reference_name_with_number = re.compile(f'^{reference}_([0-9]+)$')
            numbers = []
            for name in self._cached['catalogs']:
                matches = reference_name_with_number.match(name)
                if matches:
                    numbers.append(int(matches[1]))

            number_to_change = max(numbers) + 1 if len(numbers) else 1
            new_reference = f"{reference}_{number_to_change}"

            return new_reference
        except Exception as exc:
            print("Error while finding a new reference for new catalog")
            raise exc

    # endregion

    # region ## StoreCollection Operations ##

    def create_store_collection(self, display_name: str, reference: str) -> StoreCollection:
        """
        Make a collection into the children catalog

        :param display_name: display name of the new created

        :param reference: reference of the new created
        """
        try:
            reference = slugify(reference)
            collection = self._create_store_collection(display_name=display_name, reference=reference)

            return collection
        except Exception as exc:
            raise exc

    def _create_store_collection(self, display_name: str, reference: str, **kwargs) -> StoreCollection:
        try:
            # check if the new collection is default one?
            is_default_collection = kwargs.get('default')
            if is_default_collection is None:
                is_default_collection = False

            # make collection
            collection = StoreCollection.make_collection(
                reference=reference,
                display_name=display_name,
                default=is_default_collection
            )

            return collection
        except Exception as exc:
            raise exc

    def _add_collection_to_catalog(self, collection: StoreCollection, dest: StoreCatalog, **kwargs):
        """
        Internal method for adding a collection to a catalog. All the children products will be added accordingly.

        :param collection: the collection to be added
        :param dest: destination catalog
        :param kwargs: some options
        """
        # `keep_default` is the flag to specify that the default collection in the destination catalog will be keep or
        # not. It `True` is passed, the default collection in the destination catalog will be keep, all the new
        # collections to be copied will be mark as non default. Else, the default collection in the destination
        # catalog will be mark as non default. The default one will be copied.
        # Default is set to `True`
        try:
            new_reference_if_duplicated = kwargs.get('new_reference_if_duplicated')
            if new_reference_if_duplicated is None:
                new_reference_if_duplicated = False

            if new_reference_if_duplicated:
                if dest.has_collection_reference(reference=collection.reference):
                    collection.reference = dest.next_collection_reference(base_reference=collection.reference)

            collection.store = self
            collection.catalog = dest

            dest.add_collection(collection)

            return True
        except Exception as exc:
            raise exc

    def delete_collection(self, collection_reference: StoreCollectionReference,
                          catalog_reference: StoreCatalogReference, remove_completely: bool = False) -> None:
        """
        Delete a collection by its reference

        :param collection_reference: specify the reference of the collection to be deleted
        :param catalog_reference:
        :param remove_completely: remove completely its content or not?
        """
        try:
            catalog = self._fetch_catalog_by_reference(catalog_reference=catalog_reference)
            if not catalog:
                raise Exception(ExceptionMessages.STORE_CATALOG_NOT_FOUND)

            collection_to_delete = catalog.get_collection_by_reference(collection_reference=collection_reference)
            if not collection_to_delete:
                raise Exception(ExceptionMessages.STORE_COLLECTION_NOT_FOUND)

            if collection_to_delete.default:
                raise Exception(ExceptionMessages.DEFAULT_STORE_COLLECTION_CANNOT_BE_DELETED)

            if not remove_completely:
                default_collection = catalog.default_collection  # type: StoreCollection
                self._move_collection_content(source=collection_to_delete, dest=default_collection)

            # delete the collection
            self._delete_collection(collection=collection_to_delete, catalog=catalog)

            # raise the event
            self._raise_collection_deleted_event(collection=collection_to_delete, catalog=catalog,
                                                 delete_completely=remove_completely)
        except Exception as exc:
            raise exc

    def _move_collection_content(self, source: StoreCollection, dest: StoreCollection) -> None:
        try:
            while len(source.products):
                product = source.products.pop()

                # add to destination
                self._add_product_to_collection(product=product, dest=dest)

                # raise event
                self._raise_product_created_event(product=product)
        except Exception as exc:
            raise exc

    def _delete_collection(self, collection: StoreCollection, catalog: StoreCatalog) -> None:
        """
        Internal method to delete Collection

        :param collection:
        :param catalog: the parent catalog
        """
        try:
            catalog.collections.remove(collection)
        except Exception as exc:
            raise exc

    def update_collection(self, catalog_reference: StoreCatalogReference,
                          collection_reference: StoreCollectionReference, update_data: Dict) -> None:
        try:
            catalog = self._fetch_catalog_by_reference(catalog_reference=catalog_reference)
            if not catalog:
                raise Exception(ExceptionMessages.STORE_CATALOG_NOT_FOUND)

            collection = catalog.get_collection_by_reference(collection_reference=collection_reference)
            if not collection:
                raise Exception(ExceptionMessages.STORE_COLLECTION_NOT_FOUND)

            if collection.default and 'disabled' in update_data.keys():
                update_data.pop('disabled')

            self._update_collection(collection=collection, update_data=update_data)
        except Exception as exc:
            raise exc

    def _update_collection(self, collection: StoreCollection, update_data: Dict) -> None:
        try:
            for key, value in update_data.items():
                setattr(collection, key, value)

            self._record_event(StoreCollectionUpdatedEvent(
                store_id=self.store_id,
                catalog_id=collection.catalog.catalog_id,
                collection_id=collection.collection_id,
                collection_reference=collection.reference,
                disabled=collection.disabled
            ))
        except Exception as exc:
            raise exc

    def toggle_collection(self, catalog_reference: StoreCatalogReference,
                          collection_reference: StoreCollectionReference) -> None:
        """
        Toggle disable/ enable property of a `StoreCollection`. Input can be an instance of `StoreCollection` or
        `StoreCollectionReference`. For examples:

        collection = StoreCollection(...)
        store.toggle_collection(collection)
        store.toggle_collection(collection.reference, catalog_reference=collection.catalog.reference)

        If the collection is specified by its reference, then the catalog_reference is need too

        :param catalog_reference:
        :param collection_reference:

        """
        try:
            catalog = self._fetch_catalog_by_reference(catalog_reference=catalog_reference)
            if not catalog:
                raise Exception(ExceptionMessages.STORE_CATALOG_NOT_FOUND)

            collection = catalog.get_collection_by_reference(collection_reference=collection_reference)
            if not collection:
                raise Exception(ExceptionMessages.STORE_COLLECTION_NOT_FOUND)

            if collection.default:
                raise Exception(ExceptionMessages.DEFAULT_STORE_COLLECTION_CANNOT_BE_DISABLED)

            self._toggle_collection(collection=collection)
        except Exception as exc:
            raise exc

    def _toggle_collection(self, collection: StoreCollection) -> None:
        try:
            collection.toggle()

            self._record_event(StoreCollectionToggledEvent(
                store_id=self.store_id,
                catalog_id=collection.catalog.catalog_id,
                collection_id=collection.collection_id,
                collection_reference=collection.reference,
                disabled=collection.disabled
            ))
        except Exception as exc:
            raise exc

    def set_collection_to_default(self, collection_reference: StoreCollectionReference,
                                  catalog_reference: StoreCatalogReference) -> None:
        try:
            catalog = self._fetch_catalog_by_reference(catalog_reference=catalog_reference)
            if not catalog:
                raise Exception(ExceptionMessages.STORE_CATALOG_NOT_FOUND)

            collection = catalog.get_collection_by_reference(collection_reference=collection_reference)
            if not collection:
                raise Exception(ExceptionMessages.STORE_COLLECTION_NOT_FOUND)

            if not collection.default:
                self._set_collection_to_default(collection=collection, catalog=catalog)
        except Exception as exc:
            raise exc

    def _set_collection_to_default(self, collection: StoreCollection, catalog: StoreCatalog) -> None:
        try:
            for _collection in catalog.collections:
                _collection.default = False

            collection.default = True
            collection.disabled = False
        except Exception as exc:
            raise exc

    # endregion

    # region ## StoreBrand Operations ##
    def _try_to_get_brand(
            self,
            reference: StoreProductBrandReference,
            display_name: str
    ) -> Optional[StoreProductBrand]:
        if display_name:
            reference = slugify(reference) if reference else slugify(display_name)

        if reference:
            try:
                brand = next(b for b in self._brands if b.reference == reference)  # type: StoreProductBrand
            except StopIteration:
                brand = StoreProductBrand(reference=reference, display_name=display_name)

            return brand
        else:
            return None

    def _try_to_make_unit(
            self,
            unit: str,
            base_unit: str = None,
            conversion_factor: float = 0,
            default: bool = False,
            disabled: bool = False) -> StoreProductUnit:
        unit = StoreProductUnit(
            unit=unit,
            conversion_factor=conversion_factor,
            default=default,
            disabled=disabled,
            from_unit=base_unit
        )

        return unit

    def _try_to_make_tags(self, tags: List[str]) -> List[StoreProductTag]:
        compiled_tags = []
        for tag in tags:
            compiled_tags.append(
                StoreProductTag(tag=tag)
            )

        return compiled_tags

    # endregion

    # region ## StoreProduct Operations ##

    def make_product(
            self,
            display_name: str,
            catalog_reference: StoreCatalogReference = '',
            catalog_display_name: str = '',
            collection_reference: StoreCollectionReference = '',
            collection_display_name: str = '',
            **kwargs,
    ) -> StoreProduct:
        try:
            # make product creating params
            product_params = {}

            # try to get catalog or make new one
            catalog = self._try_get_catalog_or_create(reference=catalog_reference,
                                                      display_name=catalog_display_name)

            # try to get collection or make new one
            collection = self._try_get_collection_or_create(parent_catalog=catalog,
                                                            collection_reference=collection_reference,
                                                            collection_display_name=collection_display_name)

            product_params['catalog'] = catalog
            product_params['collection'] = collection

            # make brand
            brand_reference = kwargs.get('brand_reference')
            brand_display_name = kwargs.get('brand_display_name')
            brand = self._try_to_get_brand(
                reference=brand_reference,
                display_name=brand_display_name)  # type: StoreProductBrand
            if brand:
                brand.store = self
                self.brands.add(brand)
                product_params['brand'] = brand

            # make unit
            default_unit = kwargs.get('default_unit')
            if default_unit:
                unit = self._try_to_make_unit(unit=default_unit, default=True)
                product_params['default_unit'] = unit

            # make tags
            tags = kwargs.get('tags')
            if tags:
                if type(tags) is str:
                    tags = [tags]

                compiled_tags = self._try_to_make_tags(tags=tags)  # type:List[StoreProductTag]
                product_params['tags'] = compiled_tags

            # get product_reference
            reference = kwargs.get('reference')
            if not reference:
                reference = slugify(display_name)

            # make product
            product = self._make_product(reference=reference, display_name=display_name,
                                         **product_params)

            # make secondary units
            secondary_units = kwargs.get('unit_conversions')
            if secondary_units:
                for make_unit_request in secondary_units:  # type:CreatingStoreProductUnitConversionRequest
                    unit = product.try_to_make_unit(unit=make_unit_request.unit,
                                                    base_unit=make_unit_request.base_unit,
                                                    conversion_factor=make_unit_request.conversion_factor)
                    product.units.add(unit)

            # add it to collection
            self._add_product_to_collection(product=product, dest=collection)

            return product
        except Exception as exc:
            raise exc

    def _make_product(self, reference: StoreProductReference, display_name: str, **params) -> StoreProduct:
        try:
            catalog = params.get('catalog')
            collection = params.get('collection')

            product = StoreProduct.create_product(
                reference=reference,
                display_name=display_name,
                catalog=catalog,
                collection=collection,
                store=self
            )

            # brand
            brand = params.get('brand')
            if brand and type(brand) is StoreProductBrand:
                product.brand = brand

            # set product's default unit
            default_unit = params.get('default_unit')
            if default_unit and type(default_unit) is StoreProductUnit:
                default_unit.product = product
                product.default_unit = default_unit

            secondary_units = params.get('secondary_units')
            if secondary_units and type(secondary_units) is list:
                for conversion_unit in secondary_units:  # type: StoreProductUnit
                    ...
                    conversion_unit.product = product
                    product.units.add(conversion_unit)

            # set tags
            tags = params.get('tags')
            if tags and type(tags) is list:
                for tag in tags:
                    tag.product = product
                product.tags = tags

            # image
            image = params.get('image')
            if image:
                product.image = image

            return product
        except Exception as exc:
            raise exc

    def _add_product_to_collection(self, product: StoreProduct, dest: StoreCollection, **kwargs):
        """
        Internal method for adding a collection to a catalog. All the children products will be added accordingly.

        :param collection: the collection to be added
        :param dest: destination catalog
        :param kwargs: some options
        """
        # `keep_default` is the flag to specify that the default collection in the destination catalog will be keep or
        # not. It `True` is passed, the default collection in the destination catalog will be keep, all the new
        # collections to be copied will be mark as non default. Else, the default collection in the destination
        # catalog will be mark as non default. The default one will be copied.
        # Default is set to `True`
        keep_default = kwargs.get('keep_default') if 'keep_default' in kwargs.keys() else True

        try:
            product.collection = dest
            product.catalog = dest.catalog
            dest.add_product(product, keep_default=keep_default)
        except Exception as exc:
            raise exc

    # endregion

    # region ## Events Emitter ##

    def _raise_store_created_event(self) -> None:
        """
        Raise all the events related to the newly created store
        """
        self._record_event(StoreCreatedEvent(
            store_id=self.store_id,
            store_name=self.name,
            owner_name=self._owner.email,
            owner_email=self._owner.email,
        ))

        for catalog in self._catalogs:
            self._raise_catalog_created_event(catalog)

    def _raise_catalog_created_event(self, catalog: StoreCatalog):
        """
        Raise all the events related to the newly created catalog
        :param catalog: the catalog instance
        """
        self._record_event(StoreCatalogCreatedEvent(
            store_id=self.store_id,
            catalog_id=catalog.catalog_id,
            catalog_reference=catalog.reference
        ))

        for collection in catalog.collections:
            self._raise_collection_created_event(collection)

    def _raise_catalog_delete_event(self, catalog: StoreCatalog, delete_completely: bool) -> None:
        self._record_event(StoreCatalogDeletedEvent(
            store_id=self.store_id,
            catalog_id=catalog.catalog_id,
            owner_name=self._owner.email,
            delete_completely=delete_completely
        ))

    def _raise_collection_created_event(self, collection: StoreCollection):
        self._record_event(StoreCollectionCreatedEvent(
            store_id=self.store_id,
            catalog_id=collection.catalog.catalog_id,
            collection_id=collection.collection_id,
            collection_reference=collection.reference,
        ))

    def _raise_collection_deleted_event(self, collection: StoreCollection, catalog: StoreCatalog,
                                        delete_completely: bool):
        self._record_event(StoreCollectionDeletedEvent(
            store_id=self.store_id,
            catalog_id=catalog.catalog_id,
            collection_id=collection.collection_id,
            collection_reference=collection.reference
        ))

    def _raise_product_created_event(self, product):
        pass

    # endregion

    # region ## Misc Operations ##

    def _build_cache(self) -> Dict:
        return self._cached

    # endregion
    def update_product(self, product: StoreProduct, update: Dict):
        if 'display_name' in update.keys():
            product.display_name = update['display_name']