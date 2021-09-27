#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import NewType

from foundation.value_objects import Currency

ShopId = NewType('ShopId', tp=str)
ProductId = NewType('ProductId', tp=str)
ResourceOwnerId = NewType('ResourceOwnerId', tp=str)
PriceId = NewType('PriceId', tp=str)
PurchasePriceId = NewType('PurchasePriceId', tp=str)
SellPriceId = NewType('SellPriceId', tp=str)


class GenericItemStatus(Enum):
    PENDING_CREATION = 'PendingCreation'
    NORMAL = 'NORMAL'
    DISABLED = 'DISABLED'
    DELETED = 'DELETED'


class PriceTypes(Enum):
    SELL = 'SELL',
    PURCHASE = 'PURCHASE'


@dataclass
class ResourceOwner:
    user_id: ResourceOwnerId
    email: str
    status: GenericItemStatus

    @property
    def username(self):
        return self.email


@dataclass
class Price:
    price_id: PriceId
    amount: float
    currency: Currency
    tax: float
    effective_from: date
    expired_at: date

    def __eq__(self, other):
        if not isinstance(other, Price):
            return False
        else:
            return (self.price_id == other.price_id) | (self.price_type == other.price_type)


@dataclass
class PurchasePrice(Price):
    purchase_price_id: PurchasePriceId


@dataclass
class SellPrice(Price):
    sell_price_id: SellPriceId


class ExceptionMessages(Enum):
    CURRENCY_NOT_REGISTERED = 'Currency not available'
    RESOURCE_OWNER_NOT_FOUND = 'Unauthorized'
    URESOURCE_OWNER_NOT_ACTIVE = 'Owner is not active'
    PRICED_ITEM_NOT_FOUND = 'Priced Item not found'
    PRICED_ITEM_NOT_ACTIVE = 'Priced Item not active'
    OVERLAP_PURCHASE_PRICE_EXISTED = 'Overlap purchase price existed'
    OVERLAP_SELL_PRICE_EXISTED = 'Overlap sell price existed'
