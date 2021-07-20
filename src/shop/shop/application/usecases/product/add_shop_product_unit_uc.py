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
class AddingShopProductUnitRequest(BaseShopInputDto):
    product_id: ShopProductId
    unit_name: str
    referenced_unit_name: str
    conversion_factor: float


@dataclass
class AddingShopProductUnitResponse:
    product_id: ShopProductId
    unit_name: str

    # def serialize(self):
    #     return self.__dict__


class AddingShopProductUnitResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: AddingShopProductUnitResponse):
        raise NotImplementedError


class AddShopProductUnitUC:
    def __init__(self, boundary: AddingShopProductUnitResponseBoundary, uow: ShopUnitOfWork):
        self._ob = boundary
        self._uow = uow

    def execute(self, dto: AddingShopProductUnitRequest) -> None:
        with self._uow as uow:  # type:ShopUnitOfWork
            try:
                shop = get_shop_or_raise(shop_id=dto.shop_id, partner_id=dto.partner_id, uow=uow)
                product = uow.shops.get_product_by_id(product_id=dto.product_id)  # type:ShopProduct

                if not product.is_belong_to_shop(shop=shop):
                    raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_PRODUCT_NOT_FOUND)

                unit = product.create_unit(unit_name=dto.unit_name, conversion_factor=dto.conversion_factor,
                                           base_unit=dto.referenced_unit_name)  # type:ShopProductUnit

                # create response
                response_dto = AddingShopProductUnitResponse(
                    product_id=product.product_id,
                    unit_name=unit.unit_name,
                )
                self._ob.present(response_dto=response_dto)

                # commit
                product.version += 1
                uow.commit()
            except Exception as exc:
                raise exc
