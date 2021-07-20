#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from shop.application.services.shop_unit_of_work import ShopUnitOfWork
from shop.application.usecases.collection.update_store_collection_uc import UpdatingStoreCollectionResponseBoundary
from shop.domain.entities.value_objects import ShopCollectionId


@dataclass
class MakingStoreCollectionDefaultRequest:
    current_user: str
    collection_reference: ShopCollectionId


class MakeStoreCollectionDefaultUC:
    def __init__(self, ob: UpdatingStoreCollectionResponseBoundary, uow: ShopUnitOfWork):
        self._ob = ob
        self._uow = uow

    def execute(self, dto: MakingStoreCollectionDefaultRequest):
        with self._uow as uow:  # type: ShopUnitOfWork
            try:
                raise NotImplementedError
                store = get_shop_or_raise(store_owner=dto.current_user, uow=uow)
                store.set_collection_to_default(collection_reference=dto.collection_reference,
                                                catalog_reference=dto.catalog_reference)

                response_dto = UpdatingStoreCollectionResponse(status=True)
                self._ob.present(response_dto=response_dto)

                uow.commit()
            except Exception as exc:
                raise exc
