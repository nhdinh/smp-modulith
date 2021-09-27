#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from datetime import date
from typing import Optional

from foundation.events import ThingGoneInBlackHoleError
from foundation.value_objects import Money
from foundation.value_objects.currency import _get_registered_currency_or_default
from pricing.domain.value_objects import ProductId, ShopId, ExceptionMessages
from pricing.services.pricing_uow import PricingUnitOfWork
from pricing.services.uc.pricing_uc_common import get_authorize_bounded_user, get_priced_item
from web_app.serialization.dto import BaseAuthorizedRequest


@dataclass
class AddingItemPurchasePriceRequest(BaseAuthorizedRequest):
    shop_id: ShopId
    product_id: ProductId
    unit_name: str
    amount: float
    currency: str
    tax: float
    effective_from: date
    expired_on: Optional[date] = None


@dataclass
class AddingItemPurchasePriceResponse:
    pass


class AddingItemPurchasePriceResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: AddingItemPurchasePriceResponse):
        raise NotImplementedError


class AddItemPurchasePriceUC:
    def __init__(self, boundary: AddingItemPurchasePriceResponseBoundary, uow: PricingUnitOfWork):
        self._ob = boundary
        self._uow = uow

    def execute(self, dto: AddingItemPurchasePriceRequest) -> None:
        with self._uow as uow:  # type:PricingUnitOfWork
            try:
                # get currency
                currency = _get_registered_currency_or_default(currency=dto.currency)
                if not currency:
                    raise TypeError(ExceptionMessages.CURRENCY_NOT_REGISTERED)

                owner = get_authorize_bounded_user(user_id=dto.current_user_id, uow=uow)
                priced_item = get_priced_item(owner=owner, shop_id=dto.shop_id, product_id=dto.product_id, uow=uow)

                same_unit_pprices = [pprice for pprice in priced_item.purchase_prices if
                                     pprice.unit_name == dto.unit_name]
                if not same_unit_pprices:
                    priced_item.add_purchase_price(unit_name=dto.unit_name, amount=dto.amount, currency=dto.currency,
                                                   tax=dto.tax, effective_from=dto.effective_from,
                                                   expired_on=dto.expired_on)
                else:
                    raise Exception(ExceptionMessages.OVERLAP_PURCHASE_PRICE_EXISTED)

                response_dto = AddingItemPurchasePriceResponse()
                self._ob.present(response_dto=response_dto)

                priced_item.version += 1
                uow.commit()
            except Exception as exc:
                raise exc
