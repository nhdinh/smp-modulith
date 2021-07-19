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
StoreWarehouseId = NewType('StoreWarehouseId', tp=str)
ShopRegistrationId = NewType("ShopRegistrationId", tp=str)
SystemUserId = NewType("SystemUserId", tp=str)


class ShopStatus(Enum):
    NORMAL = 'Normal'
    DISABLED = 'Disabled'
    DELETED = 'Deleted'
    WAREHOUSE_YET_CREATED = 'Warehouse_yet_created'


class StoreProductAttributeTypes(Enum):
    COLLECTIONS = 'COLLECTIONS'
    BRAND = 'BRAND'
    SUPPLIERS = 'SUPPLIERS'


class SystemUserStatus(Enum):
    NORMAL = 'NORMAL'
    DISABLED = 'DISABLED'
    DELETED = 'DELETED'


class ShopUserType(Enum):
    MANAGER = 'Manager'
    ADMIN = 'Admin'


class AddressType(Enum):
    SHOP_ADDRESS = 'SHOP_ADDRESS'
    WAREHOUSE_ADDRESS = 'WAREHOUSE_ADDRESS'


class RegistrationStatus(Enum):
    REGISTRATION_WAITING_FOR_CONFIRMATION = 'RegistrationWaitingForConfirmation'
    REGISTRATION_CONFIRMED_YET_COMPLETED = 'ConfirmedButYetCompleted'
    REGISTRATION_CONFIRMED_COMPLETED = 'ConfirmedAndCreated'
    REGISTRATION_EXPIRED = 'Expired'


class ExceptionMessages(Enum):
    SHOP_OWNERSHIP_NOT_FOUND = 'Shop Ownership not found'
    FAILED_TO_CREATE_STORE_NO_OWNER = 'Store creating failed. No owner.'
    REGISTRATION_HAS_BEEN_EXPIRED = 'Store registration confirmation link has been expired'
    REGISTRATION_HAS_BEEN_CONFIRMED = 'Store registration has been confirmed'
    REGISTRATION_NOT_FOUND = 'No registration found'

    INVALID_FILE_TYPE = 'Upload invalid file type'

    CURRENT_USER_DO_NOT_HAVE_PERMISSION_ON_STORE = 'Current user do not have permission on this store'
    SHOP_NOT_FOUND = 'Store not existed or current user do not have any store created'
    SHOP_NOT_AVAILABLE = 'Store not available'

    INVALID_STORE_CATALOG_REFERENCE_FORMAT = 'CatalogReference not in corrected format'
    STORE_CATALOG_NOT_FOUND = 'Catalog not existed'
    STORE_CATALOG_EXISTED = 'Store already contains the catalog with same reference'
    SYSTEM_STORE_CATALOG_CANNOT_BE_DISABLED = 'Cannot disable system catalog'
    SYSTEM_STORE_CATALOG_CANNOT_BE_REMOVED = 'Cannot delete default catalog'

    CANNOT_MOVE_CATALOG_CONTENT_TO_ITSELF = 'Cannot move catalog content to itself'

    STORE_COLLECTION_EXISTED = 'The catalog already contained the collection with same reference'
    INVALID_STORE_COLLECTION_REFERENCE_FORMAT = 'CollectionReference not in corrected format'
    STORE_CATALOG_MUST_BE_SPECIFIED = 'CatalogReference must be specified'
    STORE_COLLECTION_NOT_FOUND = 'Collection not existed'
    DEFAULT_STORE_COLLECTION_CANNOT_BE_DISABLED = 'Cannot disable/enable default collection'
    DUPLICATED_COLLECTION_REFERENCE_WHEN_COPYING = 'Destination catalog already has collection with this reference'
    DEFAULT_STORE_COLLECTION_CANNOT_BE_DELETED = 'Cannot delete default collection'

    STORE_PRODUCT_EXISTED = 'Store has contains this product already'
    STORE_PRODUCT_NOT_FOUND = 'Product not existed'
    PRODUCT_UNIT_NOT_FOUND = 'Product unit not existed'
    PRODUCT_UNIT_EXISTED = 'Product unit has been existed'
    PRODUCT_BASE_UNIT_NOT_FOUND = 'Product unit to use as base not existed'
    CANNOT_DELETE_DEFAULT_UNIT = 'Cannot delete default unit'
    CANNOT_DELETE_DEPENDENCY_PRODUCT_UNIT = 'This product unit cannot be delete due to another unit is being depends on'
    REGISTRATION_RESEND_TOO_MUCH = 'Too much request, try again later'

    STORE_SUPPLIER_NOT_FOUND = 'Supplier not existed'