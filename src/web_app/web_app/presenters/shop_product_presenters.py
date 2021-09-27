#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import jsonify, make_response

from payments.api.responses import Response
from shop.application.usecases.product.add_shop_product_to_supplier_uc import \
    AddingShopProductToSupplierResponseBoundary, AddingShopProductToSupplierResponse
from shop.application.usecases.product.add_shop_product_uc import AddingShopProductResponseBoundary, \
    AddingShopProductRequest
from shop.application.usecases.product.add_shop_product_unit_uc import (
    AddingShopProductUnitResponse,
    AddingShopProductUnitResponseBoundary,
)
from shop.application.usecases.product.remove_store_product_attribute_uc import \
    RemovingStoreProductAttributeResponseBoundary, RemovingStoreProductAttributeResponse
from shop.application.usecases.product.remove_store_product_uc import RemovingShopProductsResponseBoundary, \
    RemovingShopProductsResponse
from shop.application.usecases.product.set_shop_products_status_uc import SettingShopProductsStatusResponseBoundary, \
    SettingShopProductsStatusResponse
from shop.application.usecases.product.update_shop_product_uc import UpdatingShopProductResponseBoundary, \
    UpdatingShopProductResponse
from shop.application.usecases.product.update_shop_product_unit_uc import (
    UpdatingShopProductUnitResponse,
    UpdatingShopProductUnitResponseBoundary,
)


class AddingShopProductUnitPresenter(AddingShopProductUnitResponseBoundary):
    response: Response

    def present(self, response_dto: AddingShopProductUnitResponse):
        self.response = make_response(jsonify(response_dto.__dict__))


class UpdatingShopProductUnitPresenter(UpdatingShopProductUnitResponseBoundary):
    response: Response

    def present(self, response_dto: UpdatingShopProductUnitResponse):
        self.response = make_response(jsonify(response_dto.__dict__))


class SettingShopProductsStatusPresenter(SettingShopProductsStatusResponseBoundary):
    response: Response

    def present(self, response_dto: SettingShopProductsStatusResponse):
        self.response = make_response(jsonify(response_dto.__dict__))


class AddingShopProductPresenter(AddingShopProductResponseBoundary):
    response: Response

    def present(self, response_dto: AddingShopProductRequest) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))


class UpdatingShopProductPresenter(UpdatingShopProductResponseBoundary):
    response: Response

    def present(self, response_dto: UpdatingShopProductResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))


class RemovingStoreProductAttributePresenter(RemovingStoreProductAttributeResponseBoundary):
    response: Response

    def present(self, response_dto: RemovingStoreProductAttributeResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))


class RemovingStoreProductPresenter(RemovingShopProductsResponseBoundary):
    response: Response

    def present(self, response_dto: RemovingShopProductsResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))


class AddingShopProductToSupplierPresenter(AddingShopProductToSupplierResponseBoundary):
    response: Response

    def present(self, response_dto: AddingShopProductToSupplierResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))