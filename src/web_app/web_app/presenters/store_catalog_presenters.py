#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc

from flask import Response, make_response, jsonify

from store.application.usecases.catalog.create_store_catalog_uc import AddingShopCatalogResponseBoundary, \
    AddingShopCatalogResponse
from store.application.usecases.catalog.remove_shop_catalog_uc import RemovingShopCatalogResponse, \
    RemovingShopCatalogResponseBoundary
from store.application.usecases.catalog.update_store_catalog_uc import UpdatingStoreCatalogResponseBoundary, \
    UpdatingStoreCatalogResponse
from store.application.usecases.collection.create_store_collection_uc import CreatingStoreCollectionResponseBoundary
from store.application.usecases.collection.update_store_collection_uc import UpdatingStoreCollectionResponse, \
    UpdatingStoreCollectionResponseBoundary
from store.application.usecases.initialize.initialize_store_with_plan_uc import InitializingStoreWithPlanResponse, \
    InitializingStoreWithPlanResponseBoundary
from store.application.usecases.product.create_store_product_uc import AddingShopProductResponseBoundary, \
    AddingShopProductRequest
from store.application.usecases.product.remove_store_product_attribute_uc import RemovingStoreProductAttributeResponse, \
    RemovingStoreProductAttributeResponseBoundary
from store.application.usecases.product.remove_store_product_uc import RemovingStoreProductResponse, \
    RemovingStoreProductResponseBoundary
from store.application.usecases.product.update_store_product_uc import UpdatingStoreProductResponseBoundary, \
    UpdatingStoreProductResponse
from store.application.usecases.store_uc_common import GenericStoreActionResponse, GenericStoreResponseBoundary


# TypedResponseBoundary = NewType('TypeResponseBoundary')


class AbstractResponseBoundary(abc.ABC):
    response: Response

    @abc.abstractmethod
    def _present(self, response_dto):
        raise NotImplementedError

    def present(self, response_dto) -> None:
        self.response = self._present(response_dto)


class GenericStoreResponsePresenter(GenericStoreResponseBoundary):
    response: Response

    def present(self, dto: GenericStoreActionResponse) -> None:
        self.response = make_response(jsonify(dto.__dict__))


class AddingShopCatalogPresenter(AddingShopCatalogResponseBoundary):
    response: Response

    def present(self, dto: AddingShopCatalogResponse) -> None:
        self.response = make_response(jsonify(dto.__dict__))


class UpdatingStoreCatalogPresenter(UpdatingStoreCatalogResponseBoundary):
    response: Response

    def present(self, response_dto: UpdatingStoreCatalogResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))


class RemovingShopCatalogPresenter(RemovingShopCatalogResponseBoundary):
    response: Response

    def present(self, response_dto: RemovingShopCatalogResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))


class CreatingStoreCollectionPresenter(CreatingStoreCollectionResponseBoundary):
    response: Response

    def present(self, response_dto: GenericStoreActionResponse) -> None:
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

    def present(self, response_dto: RemovingStoreProductResponse):
        self.response = make_response(jsonify(response_dto.__dict__))


class RemovingStoreProductAttributePresenter(RemovingStoreProductAttributeResponseBoundary):
    response: Response

    def present(self, response_dto: RemovingStoreProductAttributeResponse):
        self.response = make_response(jsonify(response_dto.__dict__))
# endregion
