#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector
from minio import Minio

from foundation.fs import FileSystem
from store.application.services.store_unit_of_work import ShopUnitOfWork
from store.application.services.user_counter_services import UserCounters
from store.application.usecases.catalog.create_store_catalog_uc import AddingShopCatalogResponseBoundary, \
    AddShopCatalogUC
from store.application.usecases.catalog.invalidate_store_catalog_cache_uc import InvalidateStoreCatalogCacheUC
from store.application.usecases.catalog.remove_shop_catalog_uc import RemovingShopCatalogResponseBoundary, \
    RemoveShopCatalogUC
from store.application.usecases.catalog.systemize_store_catalog_uc import SystemizeStoreCatalogUC
from store.application.usecases.catalog.toggle_store_catalog_uc import ToggleStoreCatalogUC
from store.application.usecases.catalog.update_store_catalog_uc import UpdatingStoreCatalogResponseBoundary, \
    UpdateStoreCatalogUC
from store.application.usecases.collection.create_store_collection_uc import CreatingStoreCollectionResponseBoundary, \
    CreateStoreCollectionUC
from store.application.usecases.collection.make_store_collection_default_uc import MakeStoreCollectionDefaultUC
from store.application.usecases.collection.toggle_store_collection_uc import ToggleStoreCollectionUC
from store.application.usecases.collection.update_store_collection_uc import UpdatingStoreCollectionResponseBoundary, \
    UpdateStoreCollectionUC
from store.application.usecases.create_store_warehouse_uc import CreatingStoreWarehouseResponseBoundary, \
    CreateStoreWarehouseUC
from store.application.usecases.initialize.confirm_shop_registration_uc import \
    ConfirmingShopRegistrationResponseBoundary, ConfirmShopRegistrationUC
from store.application.usecases.initialize.register_shop_uc import RegisteringShopResponseBoundary, RegisterShopUC
from store.application.usecases.manage.add_store_manager import AddingStoreManagerResponseBoundary, AddStoreManagerUC
from store.application.usecases.manage.create_store_address_uc import CreatingStoreAddressResponseBoundary, \
    CreateStoreAddressUC
from store.application.usecases.manage.resend_store_registration_confirmation_uc import \
    ResendingRegistrationConfirmationResponseBoundary, ResendRegistrationConfirmationUC
from store.application.usecases.manage.update_store_settings_uc import UpdatingStoreSettingsResponseBoundary, \
    UpdateStoreSettingsUC
from store.application.usecases.manage.upload_image_uc import UploadingImageResponseBoundary, UploadImageUC
from store.application.usecases.product.create_store_product_uc import AddingShopProductResponseBoundary, \
    CreateStoreProductUC
from store.application.usecases.product.remove_store_product_attribute_uc import \
    RemovingStoreProductAttributeResponseBoundary, RemoveStoreProductAttributeUC
from store.application.usecases.product.remove_store_product_uc import RemovingStoreProductResponseBoundary, \
    RemoveStoreProductUC
from store.application.usecases.product.update_store_product_uc import UpdatingStoreProductResponseBoundary, \
    UpdateStoreProductUC
from store.application.usecases.store_uc_common import GenericStoreResponseBoundary





