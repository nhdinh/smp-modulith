#!/usr/bin/env python
# -*- coding: utf-8 -*-
from enum import Enum
from typing import NewType

ShopId = NewType('ShopId', tp=str)
ShopCatalogId = NewType("ShopCatalogId", tp=str)
ShopCollectionId = NewType('ShopCollectionId', tp=str)
ShopSupplierId = NewType('ShopSupplierId', tp=str)
ShopAddressId = NewType('ShopAddressId', tp=str)
ShopProductId = NewType('ShopProductId', tp=str)
ShopWarehouseId = NewType('ShopWarehouseId', tp=str)
ShopRegistrationId = NewType("ShopRegistrationId", tp=str)
SystemUserId = NewType("SystemUserId", tp=str)
ShopBrandId = NewType("ShopBrandId", tp=str)


class ShopStatus(Enum):
    PENDING_CREATION = 'PendingCreation'
    NORMAL = 'Normal'
    DISABLED = 'Disabled'
    DELETED = 'Deleted'
    WAREHOUSE_YET_CREATED = 'Warehouse_yet_created'


class GenericShopItemStatus(Enum):
    PENDING_CREATION = 'PendingCreation'
    NORMAL = 'NORMAL'
    DISABLED = 'DISABLED'
    DELETED = 'DELETED'


class ShopProductAttributeTypes(Enum):
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


class ProductPriceStatus(Enum):
    FUTURE_EFFECT = 'EffectInFuture'
    IN_EFFECT = 'InEffect'
    EXPIRED = 'Expired'


class ExceptionMessages(Enum):
    INVALID_FILE_TYPE = 'Upload invalid file type'
    INVALID_CATALOG_ID = 'Invalid catalog ID'

    SHOP_OWNERSHIP_NOT_FOUND = 'Shop Ownership not found'
    FAILED_TO_CREATE_SHOP_NO_OWNER = 'Shop creating failed. No owner.'
    REGISTRATION_HAS_BEEN_EXPIRED = 'Shop registration confirmation link has been expired'
    REGISTRATION_HAS_BEEN_CONFIRMED = 'Shop registration has been confirmed'
    REGISTRATION_NOT_FOUND = 'No registration found'
    REGISTRATION_RESEND_TOO_MUCH = 'Too much request, try again later'
    EMAIL_HAS_BEEN_REGISTERED = 'Registration with this email has been existed'
    PHONE_NUMBER_HAS_BEEN_REGISTERED = 'Registration with this phone has been existed'
    PHONE_NUMBER_IS_NOT_VALID = 'Phone number is not valid'

    CURRENT_USER_DO_NOT_HAVE_PERMISSION_ON_SHOP = 'Current user do not have permission on this shop'
    SHOP_NOT_FOUND = 'Shop not existed or current user do not have any shop created'
    SHOP_NOT_AVAILABLE = 'Shop not available'

    INVALID_STORE_CATALOG_REFERENCE_FORMAT = 'CatalogReference not in corrected format'
    SHOP_CATALOG_NOT_FOUND = 'Catalog not existed'
    SHOP_CATALOG_EXISTED = 'Shop already contains the catalog with same reference'
    SYSTEM_SHOP_CATALOG_CANNOT_BE_DISABLED = 'Cannot disable system catalog'
    SYSTEM_SHOP_CATALOG_CANNOT_BE_REMOVED = 'Cannot delete default catalog'

    CANNOT_MOVE_CATALOG_CONTENT_TO_ITSELF = 'Cannot move catalog content to itself'

    SHOP_COLLECTION_EXISTED = 'The catalog already contained the collection with same reference'
    SHOP_CATALOG_MUST_BE_SPECIFIED = 'CatalogReference must be specified'
    SHOP_COLLECTION_NOT_FOUND = 'Collection not existed'
    DEFAULT_SHOP_COLLECTION_CANNOT_BE_DISABLED = 'Cannot disable/enable default collection'
    DUPLICATED_COLLECTION_REFERENCE_WHEN_COPYING = 'Destination catalog already has collection with this reference'
    DEFAULT_SHOP_COLLECTION_CANNOT_BE_DELETED = 'Cannot delete default collection'

    SHOP_PRODUCT_EXISTED = 'Shop has contains this product already'
    SHOP_PRODUCT_NOT_FOUND = 'Product not existed'
    PRODUCT_UNIT_NOT_FOUND = 'Product unit not existed'
    PRODUCT_UNIT_EXISTED = 'Product unit has been existed'
    PRODUCT_BASE_UNIT_NOT_FOUND = 'Product unit to use as base not existed'
    CANNOT_DELETE_DEFAULT_UNIT = 'Cannot delete default unit'
    CANNOT_DELETE_DEPENDENCY_PRODUCT_UNIT = 'This product unit cannot be delete due to another unit is being depends on'

    SHOP_SUPPLIER_NOT_FOUND = 'Supplier not existed'
    CURRENCY_NOT_REGISTERED = 'Currency is not registered'

    WRONG_DATA_TYPE_FOR_COMPARISON = 'Cannot compare two objects of different types'
    WRONG_DATA_TYPE_FOR_OPERATE = 'Cannot operate math on two objects of different types'
    UNSUPPORTED_OPERATION = 'Unsupported operation'

    UNSUPPORTED_FILE_TYPE = 'Unsupported file type'
