#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from typing import List, Dict, Optional

from product_catalog.domain.value_objects import ProductId
from shop.application.services.shop_unit_of_work import ShopUnitOfWork
from shop.application.usecases.shop_uc_common import get_shop_or_raise
from shop.domain.entities.shop_product import ShopProduct
from shop.domain.entities.value_objects import GenericShopItemStatus, ExceptionMessages
from web_app.serialization.dto import BaseAuthorizedShopUserRequest


@dataclass
class DisablingShopProductsRequest(BaseAuthorizedShopUserRequest):
    products: List[ProductId]


@dataclass
class DisablingShopProductsResponse:
    products: Dict[ProductId, Optional[GenericShopItemStatus]]


class DisablingShopProductsResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: DisablingShopProductsResponse):
        raise NotImplementedError


class DisableShopProductsUC:
    def __init__(self, ob: DisablingShopProductsResponseBoundary, uow: ShopUnitOfWork):
        self._ob = ob
        self._uow = uow

    def execute(self, dto: DisablingShopProductsRequest):
        if len(dto.products) > 25:
            raise Exception(ExceptionMessages.CANNOT_PROCESS_LARGE_SELECTION_OF_PRODUCTS)

        with self._uow as uow:  # type:ShopUnitOfWork
            try:
                shop = get_shop_or_raise(shop_id=dto.shop_id, user_id=dto.current_user_id, uow=uow)

                processed = dict()
                for product_id in dto.products:
                    product_id = str(product_id)
                    product = uow.shops.get_product_by_id(product_id=product_id)  # type:ShopProduct

                    if product and product.status not in [GenericShopItemStatus.DISABLED,
                                                          GenericShopItemStatus.DELETED]:
                        product.status = GenericShopItemStatus.DISABLED
                        product.version += 1
                        processed[product_id] = product.status
                    else:
                        processed[product_id] = 'UNPROCESSED'

                response_dto = DisablingShopProductsResponse(products=processed)
                self._ob.present(response_dto=response_dto)

                shop.version += 1
                uow.commit()
            except Exception as exc:
                raise exc
