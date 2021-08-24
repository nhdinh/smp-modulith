#!/usr/bin/env python
# -*- coding: utf-8 -*-
import flask_injector
import injector
from flask import Blueprint, request, Response, make_response, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from shop.application.queries.brand_queries import ListShopBrandsRequest, ListShopBrandsQuery
from web_app.helpers import validate_request_timestamp
from web_app.presenters import log_error
from web_app.serialization.dto import get_dto

SHOP_BRAND_BLUEPRINT_NAME = 'shop_brand_blueprint'
shop_brand_blueprint = Blueprint(SHOP_BRAND_BLUEPRINT_NAME, __name__)


class ShopBrandAPI(injector.Module):
    ...


@shop_brand_blueprint.route('/list', methods=['POST', 'GET'])
@validate_request_timestamp
@jwt_required()
@log_error()
def list_shop_brands(list_shop_product_brands_query: ListShopBrandsQuery) -> Response:
    dto = get_dto(request, ListShopBrandsRequest, context={'current_user_id': get_jwt_identity()})
    brands = list_shop_product_brands_query.query(dto)

    return make_response(jsonify(brands)), 200  # type:ignore
