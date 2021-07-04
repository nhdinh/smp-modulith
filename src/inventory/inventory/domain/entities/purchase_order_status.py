#!/usr/bin/env python
# -*- coding: utf-8 -*-
from enum import Enum


class PurchaseOrderStatus(Enum):
    DRAFT = 'DRAFT'
    APPROVED = 'APPROVED'
    DECLINED = 'DECLINED'
    PROCESSING = 'PROCESSING'
    COMPLETED = 'COMPLETED'
    COMPLETED_PARTLY = 'COMPLETED_PARTLY'
    FAILED = 'FAILED'