#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from enum import Enum
from typing import NewType

ShopId = NewType('ShopId', tp=str)
ProductId = NewType('ProductId', tp=str)
ResourceOwnerId = NewType('ResourceOwnerId', tp=str)


class GenericItemStatus(Enum):
    PENDING_CREATION = 'PendingCreation'
    NORMAL = 'NORMAL'
    DISABLED = 'DISABLED'
    DELETED = 'DELETED'


@dataclass
class ResourceOwner:
    user_id: ResourceOwnerId
    username: str
    status: GenericItemStatus


class ExceptionMessages(Enum):
    CURRENCY_NOT_REGISTERED = 'Currency not available'
    RESOURCE_OWNER_NOT_FOUND = 'Unauthorized'
    URESOURCE_OWNER_NOT_ACTIVE = 'Owner is not active'
    PRICED_ITEM_NOT_FOUND = 'Priced Item not found'
    PRICED_ITEM_NOT_ACTIVE = 'Priced Item not active'
    OVERLAP_PURCHASE_PRICE_EXISTED = 'Overlap purchase price existed'
    OVERLAP_SELL_PRICE_EXISTED = 'Overlap sell price existed'
