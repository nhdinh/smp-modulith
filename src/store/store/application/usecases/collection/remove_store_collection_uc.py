#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from typing import Optional

from store.domain.entities.value_objects import StoreCatalogId, StoreCollectionId

from store.application.services.store_unit_of_work import ShopUnitOfWork
from store.application.usecases.store_uc_common import get_shop_or_raise


@dataclass
class RemovingStoreCollectionResponse:
    status: bool


class RemovingStoreCollectionResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response: RemovingStoreCollectionResponse):
        raise NotImplementedError


@dataclass
class RemovingStoreCollectionRequest:
    current_user: str
    catalog_id: StoreCatalogId
    collection_id: StoreCollectionId
    remove_completely: Optional[bool] = False


class RemoveStoreCollectionUC:
    def __init__(self, boundary: RemovingStoreCollectionResponseBoundary, uow: ShopUnitOfWork):
        self._ob = boundary
        self._uow = uow

    def execute(self, dto: RemovingStoreCollectionRequest) -> None:
        with self._uow as uow:  # type: ShopUnitOfWork
            try:
                raise NotImplementedError

                # TODO: Fix this
                # store = get_shop_or_raise(store_owner=dto.current_user)
                # store.delete_collection(collection_reference=dto.collection_reference,
                #                         catalog_reference=dto.catalog_reference,
                #                         remove_completely=dto.remove_completely)
                #
                # response = RemovingStoreCollectionResponse(status=True)
                # self._ob.present(response=response)
                #
                # uow.commit()
            except Exception as exc:
                raise exc
