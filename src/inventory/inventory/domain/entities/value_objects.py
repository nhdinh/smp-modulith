#!/usr/bin/env python
# -*- coding: utf-8 -*-
from enum import Enum
from typing import NewType

WarehouseId = NewType('WarehouseId', tp=str)
PurchaseOrderId = NewType('PurchaseOrderId', tp=str)
DraftPurchaseOrderId = NewType('DraftPurchaseOrderId', tp=str)
PurchaseOrderReference = NewType('PurchaseOrderReference', tp=str)
SystemUserId = NewType("SystemUserId", tp=str)


class GenericWarehouseItemStatus(Enum):
    PENDING_CREATION = 'PendingCreation'
    NORMAL = 'NORMAL'
    DISABLED = 'DISABLED'
    DELETED = 'DELETED'


class PurchaseOrderStatus(Enum):
    DRAFT = 'DRAFT'
    APPROVED = 'APPROVED'
    DECLINED = 'DECLINED'
    PROCESSING = 'PROCESSING'
    COMPLETED = 'COMPLETED'
    COMPLETED_PARTLY = 'COMPLETED_PARTLY'
    FAILED = 'FAILED'


class WarehouseStatus(Enum):
    PENDING_CREATION = 'PendingCreation'
    NORMAL = 'Normal'
    DISABLED = 'Disabled'
    DELETED = 'Deleted'


class WarehouseUserType(Enum):
    MANAGER = 'Manager'
    ADMIN = 'Admin'


class SystemUserStatus(Enum):
    NORMAL = 'NORMAL'
    DISABLED = 'DISABLED'
    DELETED = 'DELETED'


class AddressType(Enum):
    SHOP_ADDRESS = 'SHOP_ADDRESS'
    WAREHOUSE_ADDRESS = 'WAREHOUSE_ADDRESS'
