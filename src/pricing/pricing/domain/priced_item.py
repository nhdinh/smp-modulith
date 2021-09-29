#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import date
from typing import Set

from foundation import EventMixin, Event
from foundation.events import DomainEvent, new_event_id
from foundation.value_objects import Currency
from pricing.adapter.id_generators import generate_price_id
from pricing.domain.value_objects import GenericItemStatus, Price, PriceTypes, UnitId


class PricedItem(EventMixin):
    def __init__(
            self,
            owner_id,
            shop_id,
            product_id,
            title,
            sku,
            status: GenericItemStatus = GenericItemStatus.NORMAL,
            version: int = 0
    ):
        super(PricedItem, self).__init__()

        self.product_id = product_id
        self.owner_id = owner_id
        self.shop_id = shop_id

        self.title = title
        self.sku = sku
        self.status = status
        self.version = version

        self.purchase_prices = set([])  # type:Set[Price]

    def add_purchase_price(self,
                           unit_id: UnitId,
                           unit_name: str,
                           amount: float,
                           currency: Currency,
                           tax: float,
                           effective_from: date,
                           expired_on: date):
        price_id = generate_price_id()
        price = Price(
            unit_id=unit_id,
            unit_name=unit_name,
            amount=amount,
            currency=currency,
            tax=tax,
            effective_from=effective_from,
            expired_on=expired_on,
            price_type=PriceTypes.PURCHASE
        )
        price.price_id = price_id

        if price not in self.purchase_prices:
            self.purchase_prices.add(price)

            self._record_event(DomainEvent(
                event_id=new_event_id(),
                type='PURCHASE_PRICE_CREATED',
                payload={
                    'product_id': self.product_id,
                    'unit_id': unit_id,
                    'price_id': price_id,
                }
            ))
