#!/usr/bin/env python
# -*- coding: utf-8 -*-
import flask_injector
import injector
from flask import Blueprint, request, Response, make_response, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from shop.application.queries.brand_queries import ListShopBrandsRequest, ListShopBrandsQuery, ListActiveShopBrandsQuery, \
    ListActiveShopBrandsRequest, GetBrandsCacheHashQuery
from shop.application.usecases.brand.set_shop_brands_status_uc import SetShopBrandsStatusUC, \
    SettingShopBrandsStatusResponseBoundary, SettingShopBrandsStatusRequest
from shop.application.usecases.brand.update_shop_brand_uc import UpdateShopBrandUC, UpdatingShopBrandResponseBoundary, \
    UpdatingShopBrandRequest
from web_app.helpers import validate_request_timestamp
from web_app.presenters import log_error
from web_app.presenters.shop_brand_presenters import SettingShopBrandsStatusPresenter, UpdatingShopBrandPresenter
from web_app.serialization.dto import get_dto, BaseAuthorizedShopUserRequest

SHOP_BRAND_BLUEPRINT_NAME = 'shop_brand_blueprint'
shop_brand_blueprint = Blueprint(SHOP_BRAND_BLUEPRINT_NAME, __name__)


class ShopBrandAPI(injector.Module):
    @injector.provider
    @flask_injector.request
    def set_shop_brands_status_response_boundary(self) -> SettingShopBrandsStatusResponseBoundary:
        return SettingShopBrandsStatusPresenter()

    @injector.provider
    @flask_injector.request
    def update_shop_brand_response_boundary(self) -> UpdatingShopBrandResponseBoundary:
        return UpdatingShopBrandPresenter()


@shop_brand_blueprint.route('/list', methods=['POST', 'GET'])
@validate_request_timestamp
@jwt_required()
@log_error()
def list_shop_brands(list_shop_product_brands_query: ListShopBrandsQuery) -> Response:
    dto = get_dto(request, ListShopBrandsRequest, context={'current_user_id': get_jwt_identity()})
    brands = list_shop_product_brands_query.query(dto)

    return make_response(jsonify(brands)), 200  # type:ignore


@shop_brand_blueprint.route('/list_all', methods=['POST', 'GET'])
@validate_request_timestamp
@jwt_required()
@log_error()
def list_active_shop_brands(list_active_shop_brands_query: ListActiveShopBrandsQuery) -> Response:
    dto = get_dto(request, ListActiveShopBrandsRequest, context={'current_user_id': get_jwt_identity()})
    brands = list_active_shop_brands_query.query(dto)

    return make_response(jsonify(brands)), 200  # type:ignore


@shop_brand_blueprint.route('/set_status', methods=['POST', 'PATCH'])
@validate_request_timestamp
@jwt_required()
@log_error()
def set_shop_brands_status(set_shop_brands_status_uc: SetShopBrandsStatusUC,
                           presenter: SettingShopBrandsStatusResponseBoundary) -> Response:
    dto = get_dto(request, SettingShopBrandsStatusRequest, context={'current_user_id': get_jwt_identity()})
    set_shop_brands_status_uc.execute(dto)

    return presenter.response, 201  # type:ignore


@shop_brand_blueprint.route('/update', methods=['POST', 'PATCH'])
@validate_request_timestamp
@jwt_required()
@log_error()
def update_shop_brand(update_shop_brand_uc: UpdateShopBrandUC,
                      presenter: UpdatingShopBrandResponseBoundary) -> Response:
    dto = get_dto(request, UpdatingShopBrandRequest, context={'current_user_id': get_jwt_identity()})
    update_shop_brand_uc.execute(dto)

    return presenter.response, 201  # type:ignore


@shop_brand_blueprint.route('/hash', methods=['POST', 'GET'])
@validate_request_timestamp
@jwt_required()
@log_error()
def get_brands_cache_hash(get_brands_cache_hash_query: GetBrandsCacheHashQuery) -> Response:
    dto = get_dto(request, BaseAuthorizedShopUserRequest, context={'current_user_id': get_jwt_identity()})
    hash_data = get_brands_cache_hash_query.query(dto)

    return make_response(jsonify(hash_data)), 200  # type:ignore
