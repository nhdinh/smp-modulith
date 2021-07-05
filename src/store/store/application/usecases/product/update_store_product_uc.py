#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from typing import Optional as Opt

from foundation.fs import FileSystem
from store.application.services.store_unit_of_work import StoreUnitOfWork
from store.application.usecases.const import ExceptionMessages, ExceptionOfFindingThingInBlackHole
from store.application.usecases.store_uc_common import fetch_store_by_owner_or_raise, fetch_product_by_id_or_raise
from store.domain.entities.store_product import StoreProductId


@dataclass
class UpdatingStoreProductRequest:
    current_user: str
    product_id: StoreProductId

    display_name: Opt[str]
    image: Opt[str]


@dataclass
class UpdatingStoreProductResponse:
    status: bool


class UpdatingStoreProductResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: UpdatingStoreProductResponse):
        raise NotImplementedError


class UpdateStoreProductUC:
    def __init__(self, boundary: UpdatingStoreProductResponseBoundary, uow: StoreUnitOfWork, fs: FileSystem):
        self._ob = boundary
        self._uow = uow
        self._fs = fs

    def execute(self, dto: UpdatingStoreProductRequest) -> None:
        with self._uow as uow:  # type:StoreUnitOfWork
            try:
                store = fetch_store_by_owner_or_raise(store_owner=dto.current_user, uow=uow)
                product = fetch_product_by_id_or_raise(product_id=dto.product_id, uow=uow)

                if product.collection.catalog.store != store:
                    raise ExceptionOfFindingThingInBlackHole(ExceptionMessages.STORE_PRODUCT_NOT_FOUND)

                update_data = {}

                if dto.display_name is not None:
                    update_data['display_name'] = dto.display_name

                store.update_product(product=product, update=update_data)

                response_dto = UpdatingStoreProductResponse(status=True)
                self._ob.present(response_dto=response_dto)

                uow.commit()
            except Exception as exc:
                raise exc
