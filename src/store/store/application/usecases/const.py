#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass


@dataclass(frozen=True)
class ExceptionMessages:
    FAILED_TO_CREATE_STORE_NO_OWNER = 'Store creating failed. No owner.'
    REGISTRATION_HAS_BEEN_EXPIRED = 'Store registration confirmation link has been expired'
    REGISTRATION_HAS_BEEN_CONFIRMED = 'Store registration has been confirmed'
    REGISTRATION_NOT_FOUND = 'No registration found'

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

    STORE_COLLECTION_EXISTED = 'The catalog already contained the collection with same reference'
    INVALID_STORE_COLLECTION_REFERENCE_FORMAT = 'CollectionReference not in corrected format'
    STORE_CATALOG_MUST_BE_SPECIFIED = 'CatalogReference must be specified'
    STORE_COLLECTION_NOT_FOUND = 'Collection not found'
    DEFAULT_STORE_COLLECTION_CANNOT_BE_DISABLED = 'Cannot disable/enable default collection'
    DUPLICATED_COLLECTION_REFERENCE_WHEN_COPYING = 'Destination catalog already has collection with this reference'
    DEFAULT_STORE_COLLECTION_CANNOT_BE_DELETED = 'Cannot delete default collection'


    STORE_PRODUCT_EXISTED = 'Store has contains this product already'
    STORE_PRODUCT_NOT_FOUND = 'Product not found'
    PRODUCT_UNIT_NOT_FOUND = 'Product unit not found'
    PRODUCT_UNIT_EXISTED = 'Product unit has been existed'
    PRODUCT_BASE_UNIT_NOT_FOUND = 'Product unit to use as base not found'
    CANNOT_DELETE_DEFAULT_UNIT = 'Cannot delete default unit'
    CANNOT_DELETE_DEPENDENCY_PRODUCT_UNIT = 'This product unit cannot be delete due to another unit is being depends on'
    REGISTRATION_RESEND_TOO_MUCH = 'Too much request, try again later'
