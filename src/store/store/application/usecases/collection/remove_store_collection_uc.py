#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from typing import Optional

from store.application.services.store_unit_of_work import StoreUnitOfWork
from store.application.usecases.store_uc_common import fetch_store_by_owner_or_raise
from store.domain.entities.store_catalog import StoreCatalogReference
from store.domain.entities.store_collection import StoreCollectionReference


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
    catalog_reference: StoreCatalogReference
    collection_reference: StoreCollectionReference
    remove_completely: Optional[bool] = False


class RemoveStoreCollectionUC:
    def __init__(self, boundary: RemovingStoreCollectionResponseBoundary, uow: StoreUnitOfWork):
        self._ob = boundary
        self._uow = uow

    def execute(self, dto: RemovingStoreCollectionRequest) -> None:
        with self._uow as uow:  # type: StoreUnitOfWork
            try:
                store = fetch_store_by_owner_or_raise(store_owner=dto.current_user)
                store.delete_collection(collection_reference=dto.collection_reference,
                                        catalog_reference=dto.catalog_reference,
                                        remove_completely=dto.remove_completely)

                response = RemovingStoreCollectionResponse(status=True)
                self._ob.present(response=response)

                uow.commit()
            except Exception as exc:
                raise exc
