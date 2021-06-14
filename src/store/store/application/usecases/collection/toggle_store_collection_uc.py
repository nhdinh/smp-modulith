#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from store.application.services.store_unit_of_work import StoreUnitOfWork
from store.application.usecases.collection.update_store_collection_uc import UpdatingStoreCollectionResponseBoundary, \
    UpdatingStoreCollectionResponse
from store.application.usecases.store_uc_common import fetch_store_by_owner
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
                # get store
                store = fetch_store_by_owner(store_owner=input_dto.current_user, uow=uow)

                # do update
                store.toggle_collection(catalog_reference=input_dto.catalog_reference,
                                        collection_reference=input_dto.collection_reference)

                # build the output
                response_dto = UpdatingStoreCollectionResponse(
                    status=True
                )
                self._ob.present(response_dto=response_dto)

                # commit
                uow.commit()
            except Exception as exc:
                raise exc
