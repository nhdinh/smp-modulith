#!/usr/bin/env python
# -*- coding: utf-8 -*-
from http.client import BAD_REQUEST

import flask_injector
import injector
import werkzeug.exceptions
from flask import Blueprint, Response, jsonify, make_response, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from shop.application.queries.product_queries import GetShopProductQuery, GetShopProductRequest, ListShopProductsQuery, \
    ListShopProductsRequest, ListShopProductPurchasePricesQuery, ListShopProductPurchasePricesRequest, \
    ListShopSuppliersByProductRequest, ListShopSuppliersByProductQuery, ListUnitsByShopProductQuery, \
    ListUnitsByShopProductRequest, GetShopProductPurchasePriceQuery, GetShopProductPurchasePriceRequest, \
    GetShopProductLowestPurchasePriceQuery, GetShopProductLowestPurchasePriceRequest
from shop.application.usecases.product.add_shop_product_purchase_price_uc import \
    AddingShopProductPurchasePriceResponseBoundary, AddingShopProductPurchasePriceRequest, AddShopProductPurchasePriceUC
from shop.application.usecases.product.add_shop_product_uc import (
    AddingShopProductRequest,
    AddingShopProductResponseBoundary,
    AddShopProductUC, AddingShopPendingProductRequest,
)
from shop.application.usecases.product.add_shop_product_unit_uc import (
    AddingShopProductUnitRequest,
    AddingShopProductUnitResponseBoundary,
    AddShopProductUnitUC,
)
from shop.application.usecases.product.update_shop_product_unit_uc import (
    UpdateShopProductUnitUC,
    UpdatingShopProductUnitRequest,
    UpdatingShopProductUnitResponseBoundary,
)
from web_app.presenters import log_error
from web_app.presenters.shop_catalog_presenters import AddingShopProductPresenter
from web_app.presenters.shop_product_presenters import AddingShopProductUnitPresenter, UpdatingShopProductUnitPresenter, \
    AddingShopProductPurchasePricePresenter
from web_app.serialization.dto import get_dto

SHOP_PRODUCT_BLUEPRINT_NAME = 'shop_product_blueprint'
shop_product_blueprint = Blueprint(SHOP_PRODUCT_BLUEPRINT_NAME, __name__)


class ShopProductAPI(injector.Module):
    @injector.provider
    @flask_injector.request
    def add_shop_product_response_boundary(self) -> AddingShopProductResponseBoundary:
        return AddingShopProductPresenter()

    @injector.provider
    @flask_injector.request
    def add_shop_product_unit_response_boundary(self) -> AddingShopProductUnitResponseBoundary:
        return AddingShopProductUnitPresenter()

    @injector.provider
    @flask_injector.request
    def update_shop_product_unit_response_boundary(self) -> UpdatingShopProductUnitResponseBoundary:
        return UpdatingShopProductUnitPresenter()

    @injector.provider
    @flask_injector.request
    def add_shop_product_purchase_price_response_boundary(self) -> AddingShopProductPurchasePriceResponseBoundary:
        return AddingShopProductPurchasePricePresenter()


@shop_product_blueprint.route('/add', methods=['POST'])
@jwt_required()
@log_error()
def add_shop_product(add_shop_item_uc: AddShopProductUC, presenter: AddingShopProductResponseBoundary) -> Response:
    dto = get_dto(request, AddingShopProductRequest, context={'current_user_id': get_jwt_identity()})
    add_shop_item_uc.execute(dto)

    return presenter.response, 201  # type:ignore


@shop_product_blueprint.route('/add_pending', methods=['POST'])
@jwt_required()
@log_error()
def add_shop_product_pending(add_shop_item_uc: AddShopProductUC,
                             presenter: AddingShopProductResponseBoundary) -> Response:
    dto = get_dto(request, AddingShopPendingProductRequest, context={'current_user_id': get_jwt_identity()})
    if dto.pending != 'True':
        raise werkzeug.exceptions.BadRequest
    add_shop_item_uc.execute_new_id()

    return presenter.response, 201  # type:ignore


@shop_product_blueprint.route('/list', methods=['GET', 'POST'])
@jwt_required()
@log_error()
def list_shop_products(list_shop_products_query: ListShopProductsQuery) -> Response:
    dto = get_dto(request, ListShopProductsRequest, context={'current_user_id': get_jwt_identity()})
    product = list_shop_products_query.query(dto)

    return make_response(jsonify(product)), 200  # type:ignore


@shop_product_blueprint.route('/get', methods=['GET', 'POST'])
@jwt_required()
@log_error()
def get_shop_product(get_shop_product_query: GetShopProductQuery) -> Response:
    dto = get_dto(request, GetShopProductRequest, context={'current_user_id': get_jwt_identity()})
    product = get_shop_product_query.query(dto)

    return make_response(jsonify(product)), 200  # type:ignore


@shop_product_blueprint.route('/list_units', methods=['GET', 'POST'])
@jwt_required()
@log_error()
def list_units_by_shop_product(list_units_by_shop_product_query: ListUnitsByShopProductQuery) -> Response:
    dto = get_dto(request, ListUnitsByShopProductRequest, context={'current_user_id': get_jwt_identity()})
    units = list_units_by_shop_product_query.query(dto)

    return make_response(jsonify(units)), 200  # type:ignore


@shop_product_blueprint.route('/add_unit', methods=['POST'])
@jwt_required()
@log_error()
def add_shop_product_unit(add_shop_product_unit_uc: AddShopProductUnitUC,
                          presenter: AddingShopProductUnitResponseBoundary) -> Response:
    dto = get_dto(request, AddingShopProductUnitRequest, context={'current_user_id': get_jwt_identity()})
    add_shop_product_unit_uc.execute(dto)

    return presenter.response, 201  # type:ignore


@shop_product_blueprint.route('/update_unit', methods=['POST'])
@jwt_required()
@log_error()
def update_shop_product_unit(update_shop_product_unit_uc: UpdateShopProductUnitUC,
                             presenter: UpdatingShopProductUnitResponseBoundary) -> Response:
    dto = get_dto(request, UpdatingShopProductUnitRequest, context={'current_user_id': get_jwt_identity()})
    update_shop_product_unit_uc.execute(dto)

    return presenter.response, 201  # type:ignore


@shop_product_blueprint.route('/list_suppliers', methods=['GET', 'POST'])
@jwt_required()
@log_error()
def list_shop_suppliers_by_product(list_shop_suppliers_by_product_query: ListShopSuppliersByProductQuery) -> Response:
    dto = get_dto(request, ListShopSuppliersByProductRequest, context={'current_user_id': get_jwt_identity()})
    suppliers = list_shop_suppliers_by_product_query.query(dto)

    return make_response(jsonify(suppliers)), 200  # type:ignore


@shop_product_blueprint.route('/add_purchase_price', methods=['POST'])
@jwt_required()
@log_error()
def add_shop_product_purchase_price(add_shop_product_purchase_price_uc: AddShopProductPurchasePriceUC,
                                    presenter: AddingShopProductPurchasePriceResponseBoundary) -> Response:
    dto = get_dto(request, AddingShopProductPurchasePriceRequest, context={'current_user_id': get_jwt_identity()})
    add_shop_product_purchase_price_uc.execute(dto)

    return presenter.response, 201  # type:ignore


@shop_product_blueprint.route('/list_purchase_prices', methods=['POST'])
@jwt_required()
@log_error()
def list_shop_product_purchase_prices(
        list_shop_product_purchase_prices_query: ListShopProductPurchasePricesQuery) -> Response:
    dto = get_dto(request, ListShopProductPurchasePricesRequest, context={'current_user_id': get_jwt_identity()})
    prices = list_shop_product_purchase_prices_query.query(dto)

    return make_response(jsonify(prices)), 200  # type:ignore


@shop_product_blueprint.route('/get_purchase_price', methods=['POST'])
@jwt_required()
@log_error()
def get_shop_product_purchase_price(
        get_shop_product_purchase_price_query: GetShopProductPurchasePriceQuery) -> Response:
    dto = get_dto(request, GetShopProductPurchasePriceRequest, context={'current_user_id': get_jwt_identity()})
    price = get_shop_product_purchase_price_query.query(dto)

    return make_response(jsonify(price)), 200  # type:ignore


@shop_product_blueprint.route('/get_lowest_purchase_price', methods=['POST'])
@jwt_required()
@log_error()
def get_shop_product_lowest_purchase_price(
        get_shop_product_lowest_purchase_price_query: GetShopProductLowestPurchasePriceQuery) -> Response:
    dto = get_dto(request, GetShopProductLowestPurchasePriceRequest, context={'current_user_id': get_jwt_identity()})
    price = get_shop_product_lowest_purchase_price_query.query(dto)

    return make_response(jsonify(price)), 200  # type:ignore
