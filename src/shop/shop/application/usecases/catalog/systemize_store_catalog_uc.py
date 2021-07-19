#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from shop.application.services.shop_unit_of_work import ShopUnitOfWork
from shop.application.usecases.catalog.update_shop_catalog_uc import UpdatingShopCatalogResponseBoundary, \
    UpdatingShopCatalogResponse
from shop.application.usecases.shop_uc_common import get_shop_or_raise
from shop.domain.entities.value_objects import ShopCatalogId


@dataclass
class SystemizingShopCatalogRequest:
    current_user: str
    catalog_id: ShopCatalogId


class SystemizeShopCatalogUC:
    def __init__(self, boundary: UpdatingShopCatalogResponseBoundary, uow: ShopUnitOfWork):
        self._ob = boundary
        self._uow = uow

    def execute(self, dto: SystemizingShopCatalogRequest):
        with self._uow as uow:  # type: ShopUnitOfWork
            try:
                shop = get_shop_or_raise(store_owner=dto.current_user, uow=uow)

                shop.turn_on_default_catalog(catalog_id=dto.catalog_id)

                response_dto = UpdatingShopCatalogResponse(status=True)
                self._ob.present(response_dto=response_dto)

                # increase version
                shop.version += 1

                # commit
                uow.commit()
            except Exception as exc:
                raise exc
