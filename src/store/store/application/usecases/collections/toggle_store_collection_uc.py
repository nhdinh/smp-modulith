#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from store.application.services.store_unit_of_work import StoreUnitOfWork
from store.application.usecases.collections.update_store_collection_uc import UpdatingStoreCollectionResponseBoundary, \
    UpdatingStoreCollectionResponse
from store.application.usecases.const import ExceptionMessages
from store.application.usecases.store_uc_common import is_store_disabled, validate_store_ownership
from store.domain.entities.store_catalog import StoreCatalog

from store.domain.entities.value_objects import StoreCatalogReference, StoreCollectionReference


@dataclass
class TogglingStoreCollectionRequest:
    current_user: str
    catalog_reference: StoreCatalogReference
    collection_reference: StoreCollectionReference


class ToggleStoreCollectionUC:
    def __init__(self, boundary: UpdatingStoreCollectionResponseBoundary, uow: StoreUnitOfWork):
        self._ob = boundary
        self._uow = uow

    def execute(self, input_dto: TogglingStoreCollectionRequest):
        with self._uow as uow:  # type:StoreUnitOfWork
            try:
                # fetch store data by id ID
                store = uow.stores.fetch_store_of_owner(owner=input_dto.current_user)
                if store is None:
                    raise Exception(ExceptionMessages.STORE_NOT_FOUND)

                # if the Store is disabled by admin
                if is_store_disabled(store):
                    raise Exception(ExceptionMessages.STORE_NOT_AVAILABLE)

                if not validate_store_ownership(store=store, owner_email=input_dto.current_user):
                    raise Exception(ExceptionMessages.CURRENT_USER_DO_NOT_HAVE_PERMISSION_ON_STORE)

                # check catalog
                if not store.has_catalog_reference(catalog_reference=input_dto.catalog_reference):
                    raise Exception(ExceptionMessages.STORE_CATALOG_NOT_FOUND)

                # get collection
                catalog = store.get_catalog(catalog_reference=input_dto.catalog_reference)  # type:StoreCatalog
                collection = catalog.get_collection(reference=input_dto.collection_reference)
                if not collection:
                    raise Exception(ExceptionMessages.STORE_COLLECTION_NOT_FOUND)

                if collection.default:
                    raise Exception(ExceptionMessages.DEFAULT_STORE_COLLECTION_CANNOT_BE_DISABLED)

                # do update
                store.toggle_collection(collection=collection)

                # build the output
                response_dto = UpdatingStoreCollectionResponse(
                    store_id=store.store_id,
                    catalog_reference=catalog.reference,
                    collection_reference=collection.reference,
                    disabled=collection.disabled
                )
                self._ob.present(response_dto=response_dto)

                # commit
                uow.commit()
            except Exception as exc:
                raise exc
