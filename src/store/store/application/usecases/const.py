#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass


@dataclass(frozen=True)
class ExceptionMessages:
    CURRENT_USER_DO_NOT_HAVE_PERMISSION_ON_STORE = 'Current user do not have permission on this store'
    STORE_NOT_FOUND = 'Store not found or current user do not have any store created'
    STORE_NOT_AVAILABLE = 'Store not available'

    STORE_CATALOG_NOT_FOUND = 'Catalog not found'
    STORE_CATALOG_EXISTED = 'Store already contains the catalog with same reference'
