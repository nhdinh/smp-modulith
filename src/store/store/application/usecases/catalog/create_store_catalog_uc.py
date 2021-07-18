#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from store.application.services.store_unit_of_work import ShopUnitOfWork
from store.application.usecases.const import ExceptionMessages
from store.application.usecases.store_uc_common import get_shop_or_raise
from store.domain.entities.shop_catalog import ShopCatalog
from store.domain.entities.value_objects import ShopCatalogId
from web_app.serialization.dto import BaseShopInputDto


@dataclass
class AddingShopCatalogRequest(BaseShopInputDto):
    name: str


@dataclass
class AddingShopCatalogResponse:
    catalog_id: ShopCatalogId


class AddingShopCatalogResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, dto: AddingShopCatalogResponse):
        raise NotImplementedError


class AddShopCatalogUC:
    def __init__(self, ob: AddingShopCatalogResponseBoundary, uow: ShopUnitOfWork):
        self._ob = ob
        self._uow = uow

    def execute(self, dto: AddingShopCatalogRequest):
        with self._uow as uow:  # type:ShopUnitOfWork
            try:
                shop = get_shop_or_raise(shop_id=dto.shop_id, partner_id=dto.partner_id, uow=uow)

                if shop.is_catalog_exists(title=dto.name):
                    raise Exception(ExceptionMessages.STORE_CATALOG_EXISTED)

                # make catalog
                catalog = shop.create_catalog(
                    title=dto.name,
                )  # type: ShopCatalog

                shop.catalogs.add(catalog)

                # make response
                response_dto = AddingShopCatalogResponse(catalog_id=catalog.catalog_id)
                self._ob.present(response_dto)

                shop.version += 1

                uow.commit()
            except Exception as exc:
                raise exc
