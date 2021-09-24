#!/usr/bin/env python
# -*- coding: utf-8 -*-
from enum import Enum
from typing import NewType

PromotionId = NewType('PromotionId', tp=str)


class PromotionTypes(Enum):
    ...


class PromotionStatus(Enum):
    ACTIVE = 'ACTIVE'
    DISABLED = 'DISABLED'
    DELETED = 'DELETED'
    EXPIRED = 'EXPIRED'
    PENDING = 'PENDING'
