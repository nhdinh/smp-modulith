#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from store.application.services.store_unit_of_work import ShopUnitOfWork
from store.application.usecases.catalog.update_store_catalog_uc import UpdatingStoreCatalogResponse, \
    UpdatingStoreCatalogResponseBoundary
from store.application.usecases.store_uc_common import get_shop_or_raise
from store.domain.entities.value_objects import ShopCatalogId


@dataclass
class SystemizingStoreCatalogRequest:
    current_user: str
    catalog_id: ShopCatalogId


class SystemizeStoreCatalogUC:
    def __init__(self, boundary: UpdatingStoreCatalogResponseBoundary, uow: ShopUnitOfWork):
        self._ob = boundary
        self._uow = uow

    def execute(self, dto: SystemizingStoreCatalogRequest):
        with self._uow as uow:  # type: ShopUnitOfWork
            try:
                store = get_shop_or_raise(store_owner=dto.current_user, uow=uow)

                store.turn_on_default_catalog(catalog_id=dto.catalog_id)

                response_dto = UpdatingStoreCatalogResponse(status=True)
                self._ob.present(response_dto=response_dto)

                # increase version
                store.version += 1

                # commit
                uow.commit()
            except Exception as exc:
                raise exc
