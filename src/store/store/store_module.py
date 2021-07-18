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


class ShopModule(injector.Module):
    @injector.provider
    def register_store_uc(self, boundary: RegisteringShopResponseBoundary, uow: ShopUnitOfWork,
                          user_counter_services: UserCounters) -> RegisterShopUC:
        return RegisterShopUC(boundary, uow, user_counter_services)

    @injector.provider
    def confirm_store_registration_uc(self, boundary: ConfirmingShopRegistrationResponseBoundary,
                                      uow: ShopUnitOfWork) -> ConfirmShopRegistrationUC:
        return ConfirmShopRegistrationUC(boundary, uow)

    @injector.provider
    def resend_store_registration_uc(self, boundary: ResendingRegistrationConfirmationResponseBoundary,
                                     uow: ShopUnitOfWork) -> ResendRegistrationConfirmationUC:
        return ResendRegistrationConfirmationUC(boundary, uow)

    @injector.provider
    def add_store_manager_uc(self, boundary: AddingStoreManagerResponseBoundary,
                             uow: ShopUnitOfWork) -> AddStoreManagerUC:
        return AddStoreManagerUC(boundary, uow)

    @injector.provider
    def create_store_address_uc(self, boundary: CreatingStoreAddressResponseBoundary,
                                uow: ShopUnitOfWork) -> CreateStoreAddressUC:
        return CreateStoreAddressUC(boundary, uow)

    @injector.provider
    def update_store_settings_uc(self, boundary: UpdatingStoreSettingsResponseBoundary,
                                 uow: ShopUnitOfWork) -> UpdateStoreSettingsUC:
        return UpdateStoreSettingsUC(boundary, uow)

    @injector.provider
    def create_store_warehouse_uc(self, boundary: CreatingStoreWarehouseResponseBoundary,
                                  uow: ShopUnitOfWork) -> CreateStoreWarehouseUC:
        return CreateStoreWarehouseUC(boundary, uow)

    @injector.provider
    def invalidate_store_catalog_cache_uc(self, boundary: GenericStoreResponseBoundary,
                                          uow: ShopUnitOfWork) -> InvalidateStoreCatalogCacheUC:
        return InvalidateStoreCatalogCacheUC(boundary, uow)

    @injector.provider
    def upload_image_uc(self, boundary: UploadingImageResponseBoundary, uow: ShopUnitOfWork,
                        minio_client: Minio, fs: FileSystem) -> UploadImageUC:
        return UploadImageUC(boundary, uow, minio_client, fs)

    # region ## StoreCatalog Operations ##

    @injector.provider
    def create_store_catalog_uc(self, boundary: AddingShopCatalogResponseBoundary,
                                uow: ShopUnitOfWork) -> AddShopCatalogUC:
        return AddShopCatalogUC(boundary, uow)

    @injector.provider
    def toggle_store_catalog_uc(self, boundary: UpdatingStoreCatalogResponseBoundary,
                                uow: ShopUnitOfWork) -> ToggleStoreCatalogUC:
        return ToggleStoreCatalogUC(boundary, uow)

    @injector.provider
    def remove_store_catalog_uc(self, boundary: RemovingShopCatalogResponseBoundary,
                                uow: ShopUnitOfWork) -> RemoveShopCatalogUC:
        return RemoveShopCatalogUC(boundary, uow)

    @injector.provider
    def update_store_catalog_uc(self, boundary: UpdatingStoreCatalogResponseBoundary,
                                uow: ShopUnitOfWork) -> UpdateStoreCatalogUC:
        return UpdateStoreCatalogUC(boundary, uow)

    @injector.provider
    def make_store_catalog_system_uc(self, boundary: UpdatingStoreCatalogResponseBoundary,
                                     uow: ShopUnitOfWork) -> SystemizeStoreCatalogUC:
        return SystemizeStoreCatalogUC(boundary, uow)

    # endregion

    # region ## StoreCollection Operations ##

    @injector.provider
    def create_store_collection_uc(self, boundary: CreatingStoreCollectionResponseBoundary,
                                   uow: ShopUnitOfWork) -> CreateStoreCollectionUC:
        return CreateStoreCollectionUC(boundary, uow)

    @injector.provider
    def update_store_collection_uc(self, boundary: UpdatingStoreCollectionResponseBoundary,
                                   uow: ShopUnitOfWork) -> UpdateStoreCollectionUC:
        return UpdateStoreCollectionUC(boundary, uow)

    @injector.provider
    def toggle_store_collection_uc(self, boundary: UpdatingStoreCollectionResponseBoundary,
                                   uow: ShopUnitOfWork) -> ToggleStoreCollectionUC:
        return ToggleStoreCollectionUC(boundary, uow)

    @injector.provider
    def make_store_collection_default_uc(self, boundary: UpdatingStoreCollectionResponseBoundary,
                                         uow: ShopUnitOfWork) -> MakeStoreCollectionDefaultUC:
        return MakeStoreCollectionDefaultUC(boundary, uow)

    # endregion

    # region ## StoreProduct Operation ##

    @injector.provider
    def create_store_product_uc(self, boundary: AddingShopProductResponseBoundary,
                                uow: ShopUnitOfWork) -> CreateStoreProductUC:
        return CreateStoreProductUC(boundary, uow)

    @injector.provider
    def update_store_product_uc(self, boundary: UpdatingStoreProductResponseBoundary,
                                uow: ShopUnitOfWork, fs: FileSystem) -> UpdateStoreProductUC:
        return UpdateStoreProductUC(boundary, uow, fs)

    @injector.provider
    def remove_store_product_uc(self, boundary: RemovingStoreProductResponseBoundary,
                                uow: ShopUnitOfWork, fs: FileSystem) -> RemoveStoreProductUC:
        return RemoveStoreProductUC(boundary, uow, fs)

    @injector.provider
    def remove_store_product_attribute_uc(self, boundary: RemovingStoreProductAttributeResponseBoundary,
                                          uow: ShopUnitOfWork, fs: FileSystem) -> RemoveStoreProductAttributeUC:
        return RemoveStoreProductAttributeUC(boundary, uow, fs)

    # endregion


