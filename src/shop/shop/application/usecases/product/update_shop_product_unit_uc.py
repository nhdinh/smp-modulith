#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from foundation.events import ThingGoneInBlackHoleError

from shop.application.services.shop_unit_of_work import ShopUnitOfWork
from shop.application.usecases.shop_uc_common import get_shop_or_raise
from shop.domain.entities.shop_product import ShopProduct
from shop.domain.entities.shop_product_unit import ShopProductUnit
from shop.domain.entities.value_objects import ExceptionMessages, ShopProductId
from web_app.serialization.dto import BaseShopInputDto


@dataclass
class UpdatingShopProductUnitRequest(BaseShopInputDto):
    product_id: ShopProductId
    unit_name: str
    new_unit_name: str
    conversion_factor: float


@dataclass
class UpdatingShopProductUnitResponse:
    product_id: ShopProductId
    unit_name: str

    # def serialize(self):
    #     return self.__dict__


class UpdatingShopProductUnitResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: UpdatingShopProductUnitResponse):
        raise NotImplementedError


class UpdateShopProductUnitUC:
    def __init__(self, boundary: UpdatingShopProductUnitResponseBoundary, uow: ShopUnitOfWork):
        self._ob = boundary
        self._uow = uow

    def execute(self, dto: UpdatingShopProductUnitRequest) -> None:
        with self._uow as uow:  # type:ShopUnitOfWork
            try:
                shop = get_shop_or_raise(shop_id=dto.shop_id, partner_id=dto.partner_id, uow=uow)
                product = uow.shops.get_product_by_id(product_id=dto.product_id)  # type:ShopProduct

                if not product.is_belong_to_shop(shop=shop):
                    raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_PRODUCT_NOT_FOUND)

                product.update_unit(target_unit_name=dto.unit_name, new_unit_name=dto.new_unit_name,
                                    new_conversion_factor=dto.conversion_factor)

                # create response
                response_dto = UpdatingShopProductUnitResponse(
                    product_id=product.product_id,
                    unit_name=dto.new_unit_name,
                )
                self._ob.present(response_dto=response_dto)

                # commit
                product.version += 1
                uow.commit()
            except Exception as exc:
                raise exc
