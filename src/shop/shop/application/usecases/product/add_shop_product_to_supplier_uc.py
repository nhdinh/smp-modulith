#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from foundation.events import ThingGoneInBlackHoleError

from shop.application.services.shop_unit_of_work import ShopUnitOfWork
from shop.application.usecases.shop_uc_common import get_shop_or_raise
from shop.domain.entities.shop_product import ShopProduct
from shop.domain.entities.shop_product_unit import ShopProductUnit
from shop.domain.entities.shop_supplier import ShopSupplier
from shop.domain.entities.value_objects import ExceptionMessages, ShopProductId, ShopSupplierId
from web_app.serialization.dto import BaseAuthorizedShopUserRequest


@dataclass
class AddingShopProductToSupplierRequest(BaseAuthorizedShopUserRequest):
    product_id: ShopProductId
    supplier_id: ShopSupplierId


@dataclass
class AddingShopProductToSupplierResponse:
    product_id: ShopProductId
    supplier_id: ShopSupplierId


class AddingShopProductToSupplierResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: AddingShopProductToSupplierResponse):
        raise NotImplementedError


class AddShopProductToSupplierUC:
    def __init__(self, boundary: AddingShopProductToSupplierResponseBoundary, uow: ShopUnitOfWork):
        self._ob = boundary
        self._uow = uow

    def execute(self, dto: AddingShopProductToSupplierRequest) -> None:
        with self._uow as uow:  # type:ShopUnitOfWork
            try:
                shop = get_shop_or_raise(shop_id=dto.shop_id, user_id=dto.current_user_id, uow=uow)
                product = uow.shops.get_product_by_id(product_id=dto.product_id)  # type:ShopProduct

                if not product.is_belong_to_shop(shop=shop):
                    raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_PRODUCT_NOT_FOUND)

                supplier = shop.get_supplier(supplier_id_or_name=dto.supplier_id)  # type:ShopSupplier

                if not supplier:
                    raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_SUPPLIER_NOT_FOUND)

                product.add_supplier(supplier)

                # create response
                response_dto = AddingShopProductToSupplierResponse(
                    product_id=product.product_id,
                    supplier_id=supplier.supplier_id,
                )
                self._ob.present(response_dto=response_dto)

                # commit
                product.version += 1
                uow.commit()
            except Exception as exc:
                raise exc
