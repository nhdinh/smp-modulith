#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
import itertools
from dataclasses import dataclass
from typing import Optional

from foundation import ThingGoneInBlackHoleError
from shop.application.services.shop_unit_of_work import ShopUnitOfWork
from shop.application.usecases.shop_uc_common import get_shop_or_raise
from shop.domain.entities.value_objects import ShopBrandId, ExceptionMessages
from web_app.serialization.dto import BaseAuthorizedShopUserRequest


@dataclass
class UpdatingShopBrandResponse:
    brand_id: str
    brand_name: Optional[str]
    brand_logo: Optional[str]


class UpdatingShopBrandResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: UpdatingShopBrandResponse):
        raise NotImplementedError


@dataclass
class UpdatingShopBrandRequest(BaseAuthorizedShopUserRequest):
    brand_id: ShopBrandId
    brand_name: str
    brand_logo: Optional[str] = None


class UpdateShopBrandUC:
    def __init__(self, boudary: UpdatingShopBrandResponseBoundary, uow: ShopUnitOfWork):
        self._ob = boudary
        self._uow = uow

    def execute(self, dto: UpdatingShopBrandRequest) -> None:
        with self._uow as uow:  # type: ShopUnitOfWork
            try:
                shop = get_shop_or_raise(shop_id=dto.shop_id, user_id=dto.current_user_id, uow=uow)
                brands = itertools.filterfalse(lambda b: b.brand_id != dto.brand_id, shop.brands)
                found_brands = [b for b in brands]

                if not found_brands or len(found_brands) == 0 or len(found_brands) > 1:
                    raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_BRAND_NOT_FOUND)

                brand = found_brands[0]
                brand.name = dto.brand_name
                brand.logo = dto.brand_logo

                response_dto = UpdatingShopBrandResponse(
                    brand_id=brand.brand_id,
                    brand_name=brand.name,
                    brand_logo=brand.logo,
                )
                self._ob.present(response_dto=response_dto)

                uow.commit()
            except Exception as exc:
                raise exc
