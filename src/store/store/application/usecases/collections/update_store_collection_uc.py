#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from store.application.services.store_unit_of_work import StoreUnitOfWork
from store.domain.entities.value_objects import StoreCatalogReference, StoreCollectionReference
from store.domain.entities.value_objects import StoreId


@dataclass
class UpdatingStoreCollectionRequest:
    store_id: StoreId
    catalog_reference: StoreCatalogReference
    collection_reference: StoreCollectionReference


@dataclass
class UpdatingStoreCollectionResponse:
    status: bool


class UpdatingStoreCollectionResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: UpdatingStoreCollectionResponse):
        raise NotImplementedError


class UpdateStoreCollectionUC:
    def __init__(self, ob: UpdatingStoreCollectionResponseBoundary, uow: StoreUnitOfWork):
        self._ob = ob
        self._uow = uow

    def execute(self, input_dto: UpdatingStoreCollectionRequest):
        with self._uow as uow:  # type:StoreUnitOfWork
            try:
                pass
            except Exception as exc:
                raise exc
