#!/usr/bin/env python
# -*- coding: utf-8 -*-
import flask_injector
import injector
from flask import Blueprint, Response, request, make_response, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from store.application.queries.get_shop_product_query import GetShopProductRequest, GetShopProductQuery
from store.application.usecases.product.create_store_product_uc import CreateStoreProductUC, \
    AddingShopProductResponseBoundary, AddingShopProductRequest
from web_app.presenters import log_error
from web_app.presenters.store_catalog_presenters import AddingShopProductPresenter
from web_app.serialization.dto import get_dto

SHOP_ITEM_BLUEPRINT_NAME = 'shop_product_blueprint'
shop_product_blueprint = Blueprint(SHOP_ITEM_BLUEPRINT_NAME, __name__)


class ShopProductAPI(injector.Module):
    @injector.provider
    @flask_injector.request
    def add_shop_product_response_boundary(self) -> AddingShopProductResponseBoundary:
        return AddingShopProductPresenter()


@shop_product_blueprint.route('/add', methods=['POST'])
@jwt_required()
@log_error()
def add_shop_product(add_shop_item_uc: CreateStoreProductUC, presenter: AddingShopProductResponseBoundary) -> Response:
    dto = get_dto(request, AddingShopProductRequest, context={'partner_id': get_jwt_identity()})
    add_shop_item_uc.execute(dto)

    return presenter.response, 201  # type:ignore


@shop_product_blueprint.route('/get', methods=['GET', 'POST'])
@jwt_required()
@log_error()
def get_shop_product(get_shop_product_query: GetShopProductQuery) -> Response:
    dto = get_dto(request, GetShopProductRequest, context={'partner_id': get_jwt_identity()})
    product = get_shop_product_query.query(dto)

    return make_response(jsonify(product)), 200  # type:ignore
