#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
import itertools
from dataclasses import dataclass, field
from typing import Optional

from foundation import ThingGoneInBlackHoleError
from shop.application.services.shop_unit_of_work import ShopUnitOfWork
from shop.application.usecases.shop_uc_common import get_shop_or_raise
from shop.domain.entities.value_objects import ShopCatalogId, ExceptionMessages
from web_app.serialization.dto import BaseAuthorizedShopUserRequest


@dataclass
class UpdatingShopCatalogRequest(BaseAuthorizedShopUserRequest):
    catalog_id: ShopCatalogId
    title: Optional[str] = field(repr=True, default=None)
    image: Optional[str] = field(repr=True, default=None)


@dataclass
class UpdatingShopCatalogResponse:
    catalog_id: str
    catalog_title: str
    catalog_image: str


class UpdatingShopCatalogResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: UpdatingShopCatalogResponse):
        raise NotImplementedError


class UpdateShopCatalogUC:
    def __init__(self, ob: UpdatingShopCatalogResponseBoundary, uow: ShopUnitOfWork):
        self._ob = ob
        self._uow = uow

    def execute(self, dto: UpdatingShopCatalogRequest):
        with self._uow as uow:  # type:ShopUnitOfWork
            try:
                shop = get_shop_or_raise(shop_id=dto.shop_id, user_id=dto.current_user_id, uow=uow)
                catalogs = itertools.filterfalse(lambda c: c.catalog_id != dto.catalog_id, shop.catalogs)
                found_catalogs = [c for c in catalogs]

                if not found_catalogs or len(found_catalogs) == 0 or len(found_catalogs) > 1:
                    raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_CATALOG_NOT_FOUND)

                catalog = found_catalogs[0]
                update_data = {}

                # update display_name
                if dto.title:
                    update_data['title'] = dto.title

                # update display_image
                if dto.image:
                    update_data['image'] = dto.image

                # do update
                shop.update_catalog(catalog_id=dto.catalog_id, **update_data)

                # build the output
                response_dto = UpdatingShopCatalogResponse(
                    catalog_id=catalog.catalog_id,
                    catalog_title=catalog.title,
                    catalog_image=catalog.image)
                self._ob.present(response_dto=response_dto)

                # commit
                shop.version += 1
                uow.commit()
            except Exception as exc:
                raise exc
