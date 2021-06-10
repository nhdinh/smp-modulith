#!/usr/bin/env python
# -*- coding: utf-8 -*-
from uuid import UUID

from typing import NewType

RegistrationId = NewType("RegistrationId", tp=UUID)
StoreId = NewType("StoreId", tp=UUID)

StoreOwnerId = NewType("StoreOwnerId", tp=UUID)
StoreCatalogId = NewType('StoreCatalogId', tp=UUID)
StoreCollectionId = NewType('StoreCollectionId', tp=UUID)
StoreProductId = NewType('StoreProductId', tp=UUID)

RegistrationStatus = NewType('RegistrationStatus', tp=str)

StoreCatalogReference = NewType('StoreCatalogReference', tp=str)
StoreCollectionReference = NewType('StoreCollectionReference', tp=str)
