#!/usr/bin/env python
# -*- coding: utf-8 -*-
import flask_injector
import injector
from flask import Blueprint, Response, jsonify, make_response, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from shop.application.queries.supplier_queries import (
    ListShopProductsBySupplierQuery,
    ListShopProductsBySupplierRequest,
    ListShopSuppliersQuery, ListShopSuppliersRequest,
)
from shop.application.usecases.product.add_shop_product_to_supplier_uc import (
    AddingShopProductToSupplierRequest,
    AddingShopProductToSupplierResponseBoundary,
    AddShopProductToSupplierUC,
)
from web_app.helpers import validate_request_timestamp
from web_app.presenters import log_error
from web_app.presenters.shop_catalog_presenters import AddingShopProductToSupplierPresenter
from web_app.serialization.dto import get_dto

SHOP_SUPPLIER_BLUEPRINT_NAME = 'shop_supplier_blueprint'
shop_supplier_blueprint = Blueprint(SHOP_SUPPLIER_BLUEPRINT_NAME, __name__)


class ShopSupplierAPI(injector.Module):
    @injector.provider
    @flask_injector.request
    def add_shop_product_to_supplier_response_boundary(self) -> AddingShopProductToSupplierResponseBoundary:
        return AddingShopProductToSupplierPresenter()


@shop_supplier_blueprint.route('/list', methods=['POST'])
@validate_request_timestamp
@jwt_required()
@log_error()
def list_shop_suppliers(list_shop_suppliers_query: ListShopSuppliersQuery) -> Response:
    dto = get_dto(request, ListShopSuppliersRequest, context={'current_user_id': get_jwt_identity()})
    response = list_shop_suppliers_query.query(dto)
    return make_response(jsonify(response)), 200  # type:ignore


@shop_supplier_blueprint.route('/list_products', methods=['POST'])
@validate_request_timestamp
@jwt_required()
@log_error()
def list_shop_products_by_supplier(list_shop_products_by_supplier_query: ListShopProductsBySupplierQuery) -> Response:
    dto = get_dto(request, ListShopProductsBySupplierRequest, context={'current_user_id': get_jwt_identity()})
    response = list_shop_products_by_supplier_query.query(dto)
    return make_response(jsonify(response)), 200  # type:ignore


@shop_supplier_blueprint.route('/add_product', methods=['POST'])
@validate_request_timestamp
@jwt_required()
@log_error()
def add_shop_product_to_supplier(add_shop_product_to_supplier_uc: AddShopProductToSupplierUC,
                                 presenter: AddingShopProductToSupplierResponseBoundary) -> Response:
    dto = get_dto(request, AddingShopProductToSupplierRequest, context={'current_user_id': get_jwt_identity()})
    add_shop_product_to_supplier_uc.execute(dto)

    return presenter.response, 201  # type:ignore
