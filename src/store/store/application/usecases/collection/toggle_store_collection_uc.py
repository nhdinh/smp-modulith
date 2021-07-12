#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from store.application.services.store_unit_of_work import StoreUnitOfWork
from store.application.usecases.collection.update_store_collection_uc import UpdatingStoreCollectionResponseBoundary, \
    UpdatingStoreCollectionResponse
from store.application.usecases.store_uc_common import get_shop_or_raise
from store.domain.entities.value_objects import StoreCollectionId


@dataclass
class TogglingStoreCollectionRequest:
    current_user: str
    collection_reference: StoreCollectionId


class ToggleStoreCollectionUC:
    def __init__(self, boundary: UpdatingStoreCollectionResponseBoundary, uow: StoreUnitOfWork):
        self._ob = boundary
        self._uow = uow

    def execute(self, input_dto: TogglingStoreCollectionRequest):
        with self._uow as uow:  # type:StoreUnitOfWork
            try:
                raise NotImplementedError
                # get store
                store = get_shop_or_raise(store_owner=input_dto.current_user, uow=uow)

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
