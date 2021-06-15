#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from store.application.usecases.collection.update_store_collection_uc import UpdatingStoreCollectionResponseBoundary, \
    UpdatingStoreCollectionResponse

from store.application.services.store_unit_of_work import StoreUnitOfWork
from store.application.usecases.store_uc_common import fetch_store_by_owner_or_raise
from store.domain.entities.value_objects import StoreCatalogReference, StoreCollectionReference


@dataclass
class MakingStoreCollectionDefaultRequest:
    current_user: str
    catalog_reference: StoreCatalogReference
    collection_reference: StoreCollectionReference


class MakeStoreCollectionDefaultUC:
    def __init__(self, ob: UpdatingStoreCollectionResponseBoundary, uow: StoreUnitOfWork):
        self._ob = ob
        self._uow = uow

    def execute(self, dto: MakingStoreCollectionDefaultRequest):
        with self._uow as uow:  # type: StoreUnitOfWork
            try:
                store = fetch_store_by_owner_or_raise(store_owner=dto.current_user, uow=uow)
                store.make_collection_default(collection_reference=dto.collection_reference,
                                              catalog_reference=dto.catalog_reference)

                response_dto = UpdatingStoreCollectionResponse(status=True)
                self._ob.present(response_dto=response_dto)

                uow.commit()
            except Exception as exc:
                raise exc
