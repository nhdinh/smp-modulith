#!/usr/bin/env python
# -*- coding: utf-8 -*-
from enum import Enum
from typing import NewType

PromotionId = NewType('PromotionId', tp=str)


class PromotionTypes(Enum):
    BUNDLE_DISCOUNT = 'BUNDLE_DISCOUNT', # or, Sale Combo
    BUY_X_GET_Y = 'BUY_X_GET_Y',
    BULK_DISCOUNT = 'BULK_DISCOUNT',
    CART_ADJUSTMENT = 'CART_ADJUSTMENT'
    TIME_SALE = 'TIME_SALE'



class PromotionStatus(Enum):
    ACTIVE = 'ACTIVE'
    DISABLED = 'DISABLED'
    DELETED = 'DELETED'
    EXPIRED = 'EXPIRED'
    PENDING = 'PENDING'
