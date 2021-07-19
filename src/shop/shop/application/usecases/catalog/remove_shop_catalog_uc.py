#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from typing import Optional

from shop.application.services.shop_unit_of_work import ShopUnitOfWork
from shop.application.usecases.shop_uc_common import get_shop_or_raise
from shop.domain.entities.value_objects import ShopCatalogId
from web_app.serialization.dto import BaseShopInputDto


@dataclass
class RemovingShopCatalogRequest(BaseShopInputDto):
    catalog_id: ShopCatalogId
    remove_completely: Optional[bool] = False


@dataclass
class RemovingShopCatalogResponse:
    status: bool


class RemovingShopCatalogResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response: RemovingShopCatalogResponse):
        raise NotImplementedError


class RemoveShopCatalogUC:
    def __init__(self, boundary: RemovingShopCatalogResponseBoundary, uow: ShopUnitOfWork):
        self._ob = boundary
        self._uow = uow

    def execute(self, dto: RemovingShopCatalogRequest) -> None:
        with self._uow as uow:  # type: ShopUnitOfWork
            try:
                # get input
                remove_completely = dto.remove_completely

                # get store
                shop = get_shop_or_raise(shop_id=dto.shop_id, partner_id=dto.partner_id, uow=uow)

                # delete catalog
                catalog_to_del = shop.delete_shop_catalog(
                    catalog_id=dto.catalog_id,
                    remove_completely=remove_completely
                )

                uow.session.delete(catalog_to_del)

                # release the dto
                response = RemovingShopCatalogResponse(status=True)
                self._ob.present(response)

                # commit
                uow.commit()
            except Exception as exc:
                raise exc
