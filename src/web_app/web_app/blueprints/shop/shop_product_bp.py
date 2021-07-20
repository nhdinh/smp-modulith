#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Blueprint, Response, jsonify, make_response, request
import flask_injector
from flask_jwt_extended import get_jwt_identity, jwt_required
import injector

from shop.application.queries.product_queries import GetShopProductQuery, GetShopProductRequest
from shop.application.usecases.product.add_shop_product_uc import (
    AddingShopProductRequest,
    AddingShopProductResponseBoundary,
    AddShopProductUC,
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
from web_app.presenters.shop_product_presenters import AddingShopProductUnitPresenter, UpdatingShopProductUnitPresenter
from web_app.presenters.store_catalog_presenters import AddingShopProductPresenter
from web_app.serialization.dto import get_dto

SHOP_ITEM_BLUEPRINT_NAME = 'shop_product_blueprint'
shop_product_blueprint = Blueprint(SHOP_ITEM_BLUEPRINT_NAME, __name__)


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


@shop_product_blueprint.route('/add', methods=['POST'])
@jwt_required()
@log_error()
def add_shop_product(add_shop_item_uc: AddShopProductUC, presenter: AddingShopProductResponseBoundary) -> Response:
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


@shop_product_blueprint.route('/add_unit', methods=['POST'])
@jwt_required()
@log_error()
def add_shop_product_unit(add_shop_product_unit_uc: AddShopProductUnitUC,
                          presenter: AddingShopProductUnitResponseBoundary) -> Response:
    dto = get_dto(request, AddingShopProductUnitRequest, context={'partner_id': get_jwt_identity()})
    add_shop_product_unit_uc.execute(dto)

    return presenter.response, 201  # type:ignore


@shop_product_blueprint.route('/update_unit', methods=['POST'])
@jwt_required()
@log_error()
def update_shop_product_unit(update_shop_product_unit_uc: UpdateShopProductUnitUC,
                             presenter: UpdatingShopProductUnitResponseBoundary) -> Response:
    dto = get_dto(request, UpdatingShopProductUnitRequest, context={'partner_id': get_jwt_identity()})
    update_shop_product_unit_uc.execute(dto)

    return presenter.response, 201  # type:ignore
