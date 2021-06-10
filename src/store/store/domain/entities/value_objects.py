#!/usr/bin/env python
# -*- coding: utf-8 -*-
from uuid import UUID

from typing import NewType

RegistrationId = NewType("RegistrationId", tp=UUID)
StoreId = NewType("StoreId", tp=UUID)

StoreOwnerId = NewType("StoreOwnerId", tp=UUID)

RegistrationStatus = NewType('RegistrationStatus', tp=str)

StoreCatalogId = NewType("StoreCatalogId", tp=UUID)
StoreCatalogReference = NewType('StoreCatalogReference', tp=str)

StoreCollectionId = NewType('StoreCollectionId', tp=UUID)
StoreCollectionReference = NewType('StoreCollectionReference', tp=str)

StoreProductId = NewType('StoreProductId', tp=UUID)
