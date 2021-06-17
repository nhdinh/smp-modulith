#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass


@dataclass(frozen=True)
class ExceptionMessages:
    INVALID_FILE_TYPE = 'Upload invalid file type'

    CURRENT_USER_DO_NOT_HAVE_PERMISSION_ON_STORE = 'Current user do not have permission on this store'
    STORE_NOT_FOUND = 'Store not found or current user do not have any store created'
    STORE_NOT_AVAILABLE = 'Store not available'

    INVALID_STORE_CATALOG_REFERENCE_FORMAT = 'CatalogReference not in corrected format'
    STORE_CATALOG_NOT_FOUND = 'Catalog not found'
    STORE_CATALOG_EXISTED = 'Store already contains the catalog with same reference'
    SYSTEM_STORE_CATALOG_CANNOT_BE_DISABLED = 'Cannot disable system catalog'
    SYSTEM_STORE_CATALOG_CANNOT_BE_REMOVED = 'Cannot delete default catalog'

    CANNOT_MOVE_CATALOG_CONTENT_TO_ITSELF = 'Cannot move catalog content to itself'

    INVALID_STORE_COLLECTION_REFERENCE_FORMAT = 'CollectionReference not in corrected format'
    STORE_CATALOG_MUST_BE_SPECIFIED = 'CatalogReference must be specified'
    STORE_COLLECTION_NOT_FOUND = 'Collection not found'
    DEFAULT_STORE_COLLECTION_CANNOT_BE_DISABLED = 'Cannot disable/enable default collection'
    DUPLICATED_COLLECTION_REFERENCE_WHEN_COPYING = 'Destination catalog already has collection with this reference'
    DEFAULT_STORE_COLLECTION_CANNOT_BE_DELETED = 'Cannot delete default collection'
