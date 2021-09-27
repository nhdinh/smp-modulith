#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import NewType

from foundation.value_objects import Currency

ShopId = NewType('ShopId', tp=str)
ProductId = NewType('ProductId', tp=str)
UnitId = NewType('UnitId', tp=str)
ResourceOwnerId = NewType('ResourceOwnerId', tp=str)
PriceId = NewType('PriceId', tp=str)
PurchasePriceId = NewType('PurchasePriceId', tp=str)
SellPriceId = NewType('SellPriceId', tp=str)


class GenericItemStatus(Enum):
    PENDING_CREATION = 'PendingCreation'
    NORMAL = 'NORMAL'
    DISABLED = 'DISABLED'
    DELETED = 'DELETED'


class PriceStatus(Enum):
    NORMAL = 'NORMAL'
    DISABLED = 'DISABLED'
    DELETED = 'DELETED'
    EXPIRED = 'EXPIRED'


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
class MeasurementUnit:
    unit_id: UnitId
    unit_name: str

    def __eq__(self, other):
        if not isinstance(other, MeasurementUnit):
            return False
        else:
            return other.unit_id == self.unit_id or (
                    other.product_id == self.product_id and other.unit_name == self.unit_name)


@dataclass
class Price:
    unit_id: UnitId
    unit_name: str
    amount: float
    currency: Currency
    tax: float
    effective_from: date
    expired_on: date
    price_type: PriceTypes

    @property
    def price_id(self):
        return self._price_id

    @price_id.setter
    def price_id(self, value):
        if value:
            self._price_id = value
        else:
            raise ValueError('PriceId must not be null')

    def __hash__(self):
        return hash((self.product_id, self.unit_id, self._price_id, self.price_type))

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
