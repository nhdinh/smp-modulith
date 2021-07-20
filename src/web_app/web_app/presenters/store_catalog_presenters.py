#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc

from flask import Response, jsonify, make_response

from shop.application.usecases.catalog.add_shop_catalog_uc import (
    AddingShopCatalogResponse,
    AddingShopCatalogResponseBoundary,
)
from shop.application.usecases.catalog.remove_shop_catalog_uc import (
    RemovingShopCatalogResponse,
    RemovingShopCatalogResponseBoundary,
)
from shop.application.usecases.catalog.update_shop_catalog_uc import (
    UpdatingShopCatalogResponse,
    UpdatingShopCatalogResponseBoundary,
)
from shop.application.usecases.collection.create_store_collection_uc import CreatingStoreCollectionResponseBoundary
from shop.application.usecases.collection.update_store_collection_uc import (
    UpdatingStoreCollectionResponse,
    UpdatingStoreCollectionResponseBoundary,
)
from shop.application.usecases.initialize.initialize_store_with_plan_uc import (
    InitializingStoreWithPlanResponse,
    InitializingStoreWithPlanResponseBoundary,
)
from shop.application.usecases.product.add_shop_product_to_supplier_uc import (
    AddingShopProductToSupplierResponse,
    AddingShopProductToSupplierResponseBoundary,
)
from shop.application.usecases.product.add_shop_product_uc import (
    AddingShopProductRequest,
    AddingShopProductResponseBoundary,
)
from shop.application.usecases.product.remove_store_product_attribute_uc import (
    RemovingStoreProductAttributeResponse,
    RemovingStoreProductAttributeResponseBoundary,
)
from shop.application.usecases.product.remove_store_product_uc import (
    RemovingStoreProductResponse,
    RemovingStoreProductResponseBoundary,
)
from shop.application.usecases.product.update_store_product_uc import (
    UpdatingStoreProductResponse,
    UpdatingStoreProductResponseBoundary,
)
from shop.application.usecases.shop_uc_common import GenericShopActionResponse, GenericShopResponseBoundary


class AbstractResponseBoundary(abc.ABC):
    response: Response

    @abc.abstractmethod
    def _present(self, response_dto):
        raise NotImplementedError

    def present(self, response_dto) -> None:
        self.response = self._present(response_dto)


class GenericStoreResponsePresenter(GenericShopResponseBoundary):
    response: Response

    def present(self, dto: GenericShopActionResponse) -> None:
        self.response = make_response(jsonify(dto.__dict__))


class AddingShopCatalogPresenter(AddingShopCatalogResponseBoundary):
    response: Response

    def present(self, dto: AddingShopCatalogResponse) -> None:
        self.response = make_response(jsonify(dto.__dict__))


class UpdatingStoreCatalogPresenter(UpdatingShopCatalogResponseBoundary):
    response: Response

    def present(self, response_dto: UpdatingShopCatalogResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))


class RemovingShopCatalogPresenter(RemovingShopCatalogResponseBoundary):
    response: Response

    def present(self, response_dto: RemovingShopCatalogResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))


class CreatingStoreCollectionPresenter(CreatingStoreCollectionResponseBoundary):
    response: Response

    def present(self, response_dto: GenericShopActionResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))


class UpdatingStoreCollectionPresenter(UpdatingStoreCollectionResponseBoundary):
    response: Response

    def present(self, response_dto: UpdatingStoreCollectionResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))


class InitializingStoreWithPlanResponsePresenter(InitializingStoreWithPlanResponseBoundary):
    response: Response

    def present(self, response_dto: InitializingStoreWithPlanResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))


# region ## Store Product Presenters ##
class AddingShopProductPresenter(AddingShopProductResponseBoundary):
    response: Response

    def present(self, response_dto: AddingShopProductRequest) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))


class UpdatingStoreProductPresenter(UpdatingStoreProductResponseBoundary):
    response: Response

    def present(self, response_dto: UpdatingStoreProductResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))


class RemovingStoreProductPresenter(RemovingStoreProductResponseBoundary):
    response: Response

    def present(self, response_dto: RemovingStoreProductResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))


class RemovingStoreProductAttributePresenter(RemovingStoreProductAttributeResponseBoundary):
    response: Response

    def present(self, response_dto: RemovingStoreProductAttributeResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))


class AddingShopProductToSupplierPresenter(AddingShopProductToSupplierResponseBoundary):
    response: Response

    def present(self, response_dto: AddingShopProductToSupplierResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))
# endregion
