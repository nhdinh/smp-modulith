#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from store.application.services.store_unit_of_work import ShopUnitOfWork
from store.application.usecases.store_uc_common import get_shop_or_raise, get_catalog_from_store_or_raise, \
    GenericStoreActionResponse
from store.domain.entities.shop import Shop
from store.domain.entities.value_objects import StoreCatalogId


@dataclass
class CreatingStoreCollectionRequest:
    current_user: str
    catalog_id: StoreCatalogId
    title: str


class CreatingStoreCollectionResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: GenericStoreActionResponse):
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
                response_dto = GenericStoreActionResponse(status=True)
                self._ob.present(response_dto=response_dto)

                # increase version of aggregate
                store.version += 1

                # commit
                uow.commit()
            except Exception as exc:
                raise exc
