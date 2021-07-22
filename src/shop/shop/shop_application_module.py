#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector
from minio import Minio

from foundation.fs import FileSystem
from shop.application.services.shop_unit_of_work import ShopUnitOfWork
from shop.application.usecases.catalog.add_shop_catalog_uc import AddingShopCatalogResponseBoundary, AddShopCatalogUC
from shop.application.usecases.catalog.invalidate_shop_catalog_cache_uc import InvalidateShopCatalogCacheUC
from shop.application.usecases.catalog.remove_shop_catalog_uc import (
    RemoveShopCatalogUC,
    RemovingShopCatalogResponseBoundary,
)
from shop.application.usecases.catalog.systemize_store_catalog_uc import SystemizeShopCatalogUC
from shop.application.usecases.catalog.toggle_store_catalog_uc import ToggleStoreCatalogUC
from shop.application.usecases.catalog.update_shop_catalog_uc import (
    UpdateStoreCatalogUC,
    UpdatingShopCatalogResponseBoundary,
)
from shop.application.usecases.catalog.add_shop_collection_uc import AddShopCollectionUC, \
    AddingShopCollectionResponseBoundary
from shop.application.usecases.collection.make_store_collection_default_uc import MakeStoreCollectionDefaultUC
from shop.application.usecases.collection.toggle_store_collection_uc import ToggleStoreCollectionUC
from shop.application.usecases.collection.update_store_collection_uc import (
    UpdateStoreCollectionUC,
    UpdatingStoreCollectionResponseBoundary,
)
from shop.application.usecases.create_store_warehouse_uc import (
    CreateStoreWarehouseUC,
    CreatingStoreWarehouseResponseBoundary,
)
from shop.application.usecases.initialize.confirm_shop_registration_uc import (
    ConfirmingShopRegistrationResponseBoundary,
    ConfirmShopRegistrationUC,
)
from shop.application.usecases.initialize.register_shop_uc import RegisteringShopResponseBoundary, RegisterShopUC
from shop.application.usecases.product.add_shop_product_to_supplier_uc import (
    AddingShopProductToSupplierResponseBoundary,
    AddShopProductToSupplierUC,
)
from shop.application.usecases.product.add_shop_product_uc import AddingShopProductResponseBoundary, AddShopProductUC
from shop.application.usecases.product.add_shop_product_unit_uc import (
    AddingShopProductUnitResponseBoundary,
    AddShopProductUnitUC,
)
from shop.application.usecases.product.remove_store_product_attribute_uc import (
    RemoveStoreProductAttributeUC,
    RemovingStoreProductAttributeResponseBoundary,
)
from shop.application.usecases.product.remove_store_product_uc import (
    RemoveStoreProductUC,
    RemovingStoreProductResponseBoundary,
)
from shop.application.usecases.product.update_shop_product_unit_uc import (
    UpdateShopProductUnitUC,
    UpdatingShopProductUnitResponseBoundary,
)
from shop.application.usecases.product.update_store_product_uc import (
    UpdateStoreProductUC,
    UpdatingStoreProductResponseBoundary,
)
from shop.application.usecases.shop.add_shop_address_uc import AddingShopAddressResponseBoundary, AddShopAddressUC
from shop.application.usecases.shop.add_shop_manager import AddingStoreManagerResponseBoundary, AddStoreManagerUC
from shop.application.usecases.shop.resend_store_registration_confirmation_uc import (
    ResendingRegistrationConfirmationResponseBoundary,
    ResendRegistrationConfirmationUC,
)
from shop.application.usecases.shop.update_store_settings_uc import (
    UpdateStoreSettingsUC,
    UpdatingStoreSettingsResponseBoundary,
)
from shop.application.usecases.shop.upload_image_uc import UploadImageUC, UploadingImageResponseBoundary
from shop.application.usecases.shop_uc_common import GenericShopResponseBoundary


class ShopApplicationModule(injector.Module):
    @injector.provider
    def register_store_uc(self, boundary: RegisteringShopResponseBoundary, uow: ShopUnitOfWork, ) -> RegisterShopUC:
        # user_counter_services: UserCounters) -> RegisterShopUC:
        return RegisterShopUC(boundary, uow)  # , user_counter_services)

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
    def add_store_address_uc(self, boundary: AddingShopAddressResponseBoundary,
                             uow: ShopUnitOfWork) -> AddShopAddressUC:
        return AddShopAddressUC(boundary, uow)

    @injector.provider
    def update_store_settings_uc(self, boundary: UpdatingStoreSettingsResponseBoundary,
                                 uow: ShopUnitOfWork) -> UpdateStoreSettingsUC:
        return UpdateStoreSettingsUC(boundary, uow)

    @injector.provider
    def create_store_warehouse_uc(self, boundary: CreatingStoreWarehouseResponseBoundary,
                                  uow: ShopUnitOfWork) -> CreateStoreWarehouseUC:
        return CreateStoreWarehouseUC(boundary, uow)

    @injector.provider
    def invalidate_shop_catalog_cache_uc(self, boundary: GenericShopResponseBoundary,
                                         uow: ShopUnitOfWork) -> InvalidateShopCatalogCacheUC:
        return InvalidateShopCatalogCacheUC(boundary, uow)

    @injector.provider
    def upload_image_uc(self, boundary: UploadingImageResponseBoundary, uow: ShopUnitOfWork,
                        minio_client: Minio, fs: FileSystem) -> UploadImageUC:
        return UploadImageUC(boundary, uow, minio_client, fs)

    # region ## StoreCatalog Operations ##

    @injector.provider
    def add_shop_catalog_uc(self, boundary: AddingShopCatalogResponseBoundary,
                            uow: ShopUnitOfWork) -> AddShopCatalogUC:
        return AddShopCatalogUC(boundary, uow)

    @injector.provider
    def toggle_shop_catalog_uc(self, boundary: UpdatingShopCatalogResponseBoundary,
                               uow: ShopUnitOfWork) -> ToggleStoreCatalogUC:
        return ToggleStoreCatalogUC(boundary, uow)

    @injector.provider
    def remove_shop_catalog_uc(self, boundary: RemovingShopCatalogResponseBoundary,
                               uow: ShopUnitOfWork) -> RemoveShopCatalogUC:
        return RemoveShopCatalogUC(boundary, uow)

    @injector.provider
    def update_shop_catalog_uc(self, boundary: UpdatingShopCatalogResponseBoundary,
                               uow: ShopUnitOfWork) -> UpdateStoreCatalogUC:
        return UpdateStoreCatalogUC(boundary, uow)

    @injector.provider
    def make_shop_catalog_system_uc(self, boundary: UpdatingShopCatalogResponseBoundary,
                                    uow: ShopUnitOfWork) -> SystemizeShopCatalogUC:
        return SystemizeShopCatalogUC(boundary, uow)

    # endregion

    # region ## StoreCollection Operations ##

    @injector.provider
    def add_shop_collection_uc(self, boundary: AddingShopCollectionResponseBoundary,
                               uow: ShopUnitOfWork) -> AddShopCollectionUC:
        return AddShopCollectionUC(boundary, uow)

    @injector.provider
    def update_shop_collection_uc(self, boundary: UpdatingStoreCollectionResponseBoundary,
                                  uow: ShopUnitOfWork) -> UpdateStoreCollectionUC:
        return UpdateStoreCollectionUC(boundary, uow)

    @injector.provider
    def toggle_shop_collection_uc(self, boundary: UpdatingStoreCollectionResponseBoundary,
                                  uow: ShopUnitOfWork) -> ToggleStoreCollectionUC:
        return ToggleStoreCollectionUC(boundary, uow)

    @injector.provider
    def make_shop_collection_default_uc(self, boundary: UpdatingStoreCollectionResponseBoundary,
                                        uow: ShopUnitOfWork) -> MakeStoreCollectionDefaultUC:
        return MakeStoreCollectionDefaultUC(boundary, uow)

    # endregion

    # region ## StoreProduct Operation ##

    @injector.provider
    def add_shop_product_uc(self, boundary: AddingShopProductResponseBoundary,
                            uow: ShopUnitOfWork) -> AddShopProductUC:
        return AddShopProductUC(boundary, uow)

    @injector.provider
    def update_shop_product_uc(self, boundary: UpdatingStoreProductResponseBoundary,
                               uow: ShopUnitOfWork, fs: FileSystem) -> UpdateStoreProductUC:
        return UpdateStoreProductUC(boundary, uow, fs)

    @injector.provider
    def remove_shop_product_uc(self, boundary: RemovingStoreProductResponseBoundary,
                               uow: ShopUnitOfWork, fs: FileSystem) -> RemoveStoreProductUC:
        return RemoveStoreProductUC(boundary, uow, fs)

    @injector.provider
    def remove_shop_product_attribute_uc(self, boundary: RemovingStoreProductAttributeResponseBoundary,
                                         uow: ShopUnitOfWork, fs: FileSystem) -> RemoveStoreProductAttributeUC:
        return RemoveStoreProductAttributeUC(boundary, uow, fs)

    @injector.provider
    def add_shop_product_unit_uc(self, boundary: AddingShopProductUnitResponseBoundary,
                                 uow: ShopUnitOfWork, ) -> AddShopProductUnitUC:
        return AddShopProductUnitUC(boundary, uow)

    @injector.provider
    def update_shop_product_unit_uc(self, boundary: UpdatingShopProductUnitResponseBoundary,
                                    uow: ShopUnitOfWork, ) -> UpdateShopProductUnitUC:
        return UpdateShopProductUnitUC(boundary, uow)

    @injector.provider
    def add_shop_product_to_supplier_uc(self, boundary: AddingShopProductToSupplierResponseBoundary,
                                        uow: ShopUnitOfWork) -> AddShopProductToSupplierUC:
        return AddShopProductToSupplierUC(boundary, uow)

    # endregion
