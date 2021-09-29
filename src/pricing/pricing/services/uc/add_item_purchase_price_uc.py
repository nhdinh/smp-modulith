#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from datetime import date
from typing import Optional

from foundation.value_objects.currency import _get_registered_currency_or_default
from pricing.domain.priced_item import PricedItem
from pricing.domain.value_objects import ProductId, ShopId, ExceptionMessages, UnitId, GenericItemStatus
from pricing.services.pricing_uow import PricingUnitOfWork
from pricing.services.uc.pricing_uc_common import get_authorize_bounded_user, get_priced_item, is_duration_overlapping
from web_app.serialization.dto import BaseAuthorizedRequest


@dataclass
class AddingItemPurchasePriceRequest(BaseAuthorizedRequest):
    shop_id: ShopId

    product_id: ProductId
    product_title: Optional[str]
    product_sku: Optional[str]
    product_status: Optional[str]

    unit_id: UnitId
    unit_name: Optional[str]

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

                priced_item = None
                try:
                    priced_item = get_priced_item(owner=owner, shop_id=dto.shop_id, product_id=dto.product_id, uow=uow)
                except Exception:
                    priced_item = PricedItem(owner_id=dto.current_user_id,
                                             shop_id=dto.shop_id,
                                             product_id=dto.product_id,
                                             title=dto.product_title,
                                             sku=dto.product_sku,
                                             status=GenericItemStatus(dto.product_status), version=0)
                    uow.prices.save(priced_item)

                same_unit_pprices = [pprice for pprice in priced_item.purchase_prices if
                                     pprice.unit_name == dto.unit_name]
                if same_unit_pprices:
                    for existed_pprice in same_unit_pprices:
                        if is_duration_overlapping(existed_pprice.effective_from, existed_pprice.expired_on,
                                                   dto.effective_from, dto.expired_on):
                            raise Exception(ExceptionMessages.OVERLAP_PURCHASE_PRICE_EXISTED)

                priced_item.add_purchase_price(unit_id=dto.unit_id,
                                               unit_name=dto.unit_name,
                                               amount=dto.amount,
                                               currency=currency.iso_code,
                                               tax=dto.tax,
                                               effective_from=dto.effective_from,
                                               expired_on=dto.expired_on)

                response_dto = AddingItemPurchasePriceResponse()
                self._ob.present(response_dto=response_dto)

                priced_item.version += 1
                uow.commit()
            except Exception as exc:
                raise exc
