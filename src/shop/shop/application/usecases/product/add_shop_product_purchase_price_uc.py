#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from datetime import date
from typing import Optional

from foundation.events import ThingGoneInBlackHoleError
from foundation.value_objects import Money
from foundation.value_objects.currency import _get_registered_currency_or_default
from shop.application.services.shop_unit_of_work import ShopUnitOfWork
from shop.application.usecases.shop_uc_common import get_shop_or_raise
from shop.domain.entities.shop_product import ShopProduct
from shop.domain.entities.value_objects import ShopProductId, ShopSupplierId, ExceptionMessages
from web_app.serialization.dto import BaseAuthorizedShopUserRequest


@dataclass
class AddingShopProductPurchasePriceRequest(BaseAuthorizedShopUserRequest):
    product_id: ShopProductId
    supplier_id: ShopSupplierId
    unit_name: str
    amount: float
    currency: str
    tax: float
    effective_from: date
    expired_on: Optional[date] = None


@dataclass
class AddingShopProductPurchasePriceResponse:
    pass


class AddingShopProductPurchasePriceResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: AddingShopProductPurchasePriceResponse):
        raise NotImplementedError


class AddShopProductPurchasePriceUC:
    def __init__(self, boundary: AddingShopProductPurchasePriceResponseBoundary, uow: ShopUnitOfWork):
        self._ob = boundary
        self._uow = uow

    def execute(self, dto: AddingShopProductPurchasePriceRequest) -> None:
        with self._uow as uow:  # type:ShopUnitOfWork
            try:
                # get currency
                currency = _get_registered_currency_or_default(currency=dto.currency)
                if not currency:
                    raise TypeError(ExceptionMessages.CURRENCY_NOT_REGISTERED)

                shop = get_shop_or_raise(shop_id=dto.shop_id, user_id=dto.current_user_id, uow=uow)
                product = uow.shops.get_product_by_id(product_id=dto.product_id)  # type:ShopProduct

                if not product:
                    raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_PRODUCT_NOT_FOUND)

                if not product.is_belong_to_shop(shop=shop):
                    raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_PRODUCT_NOT_FOUND)

                supplier = shop.get_supplier(supplier_id_or_name=dto.supplier_id)
                if not supplier:
                    raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_SUPPLIER_NOT_FOUND)

                # add supplier to product if needed
                if supplier not in product.suppliers:
                    product.suppliers.add(supplier)

                unit = product.get_unit(unit_name=dto.unit_name)
                if not unit:
                    raise ThingGoneInBlackHoleError(ExceptionMessages.PRODUCT_UNIT_NOT_FOUND)

                price = product.create_purchase_price_by_supplier(
                    supplier=supplier,
                    unit=unit,
                    price=Money(currency=currency, amount=dto.amount),
                    tax=dto.tax,
                    effective_from=dto.effective_from,
                    expired_on=dto.expired_on
                )

                response_dto = AddingShopProductPurchasePriceResponse()
                self._ob.present(response_dto=response_dto)

                product.version += 1
                uow.commit()
            except Exception as exc:
                raise exc
