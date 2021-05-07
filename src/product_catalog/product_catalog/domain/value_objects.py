#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import NewType
from uuid import UUID

CatalogId = NewType("CatalogId", tp=UUID)
CatalogReference = str

CollectionReference = str

ProductId = NewType("ProductId", tp=UUID)
ProductReference = str
