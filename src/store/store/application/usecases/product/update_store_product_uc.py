#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from store.application.services.store_unit_of_work import StoreUnitOfWork
from store.application.usecases.store_uc_common import fetch_store_by_owner_or_raise
from store.domain.entities.value_objects import StoreProductId


@dataclass
class UpdatingStoreProductRequest:
    current_user: str
    product_id: StoreProductId


@dataclass
class UpdatingStoreProductResponse:
    status: bool


class UpdatingStoreProductResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: UpdatingStoreProductResponse) -> None:
        raise NotImplementedError


class UpdateStoreProductUC:
    def __init__(self, boundary: UpdatingStoreProductResponseBoundary, uow: StoreUnitOfWork):
        self._ob = boundary
        self._uow = uow

    def execute(self, dto: UpdatingStoreProductRequest) -> None:
        with self._uow as uow:  # type:StoreUnitOfWork
            try:
                store_id = fetch_store_by_owner_or_raise(store_owner=dto.current_user, uow=uow)

            except Exception as exc:
                raise exc
