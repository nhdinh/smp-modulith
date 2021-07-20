#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from shop.application.services.shop_unit_of_work import ShopUnitOfWork
from shop.application.usecases.shop_uc_common import (
    GenericShopActionResponse,
    get_catalog_from_store_or_raise,
    get_shop_or_raise,
)
from shop.domain.entities.value_objects import ShopCatalogId


@dataclass
class CreatingStoreCollectionRequest:
    current_user: str
    catalog_id: ShopCatalogId
    title: str


class CreatingStoreCollectionResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: GenericShopActionResponse):
        raise NotImplementedError


class CreateStoreCollectionUC:
    def __init__(self, boundary: CreatingStoreCollectionResponseBoundary, uow: ShopUnitOfWork):
        self._ob = boundary
        self._uow = uow

    def execute(self, dto: CreatingStoreCollectionRequest):
        with self._uow as uow:  # type:ShopUnitOfWork
            try:
                store = get_shop_or_raise(store_owner=dto.current_user, uow=uow)  # type:Shop
                catalog = get_catalog_from_store_or_raise(catalog_id=dto.catalog_id, store=store)

                # make collection
                collection = store.make_collection(title=dto.title, parent_catalog=catalog)

                # make response
                response_dto = GenericShopActionResponse(status=True)
                self._ob.present(response_dto=response_dto)

                # increase version of aggregate
                store.version += 1

                # commit
                uow.commit()
            except Exception as exc:
                raise exc
