#!/usr/bin/env python
# -*- coding: utf-8 -*-
from enum import Enum
from typing import NewType

PurchaseOrderId = NewType('PurchaseOrderId', tp=str)
DraftPurchaseOrderId = NewType('DraftPurchaseOrderId', tp=str)
PurchaseOrderReference = NewType('PurchaseOrderReference', tp=str)


class PurchaseOrderStatus(Enum):
    DRAFT = 'DRAFT'
    APPROVED = 'APPROVED'
    DECLINED = 'DECLINED'
    PROCESSING = 'PROCESSING'
    COMPLETED = 'COMPLETED'
    COMPLETED_PARTLY = 'COMPLETED_PARTLY'
    FAILED = 'FAILED'