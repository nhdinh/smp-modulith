#!/usr/bin/env python
# -*- coding: utf-8 -*-
from enum import Enum
from typing import NewType

ShopId = NewType('StoreId', tp=str)
ShopCatalogId = NewType("StoreCatalogId", tp=str)
StoreCollectionId = NewType('StoreCollectionId', tp=str)
StoreSupplierId = NewType('StoreSupplierId', tp=str)
StoreAddressId = NewType('StoreAddressId', tp=str)
ShopProductId = NewType('StoreProductId', tp=str)


class ShopStatus(Enum):
    NORMAL = 'Normal'
    DISABLED = 'Disabled'
    DELETED = 'Deleted'
    WAREHOUSE_YET_CREATED = 'Warehouse_yet_created'
