#!/usr/bin/env python
# -*- coding: utf-8 -*-
import flask_injector
import injector
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from pricing.services.uc.add_item_purchase_price_uc import AddItemPurchasePriceUC, \
    AddingItemPurchasePriceResponseBoundary, AddingItemPurchasePriceRequest
from web_app.helpers import validate_request_timestamp
from web_app.presenters import log_error
from web_app.presenters.pricing_presenter import AddingItemPurchasePricePresenter
from web_app.serialization.dto import get_dto

PRICING_BLUEPRINT_NAME = 'pricing_blueprint'
pricing_blueprint = Blueprint(PRICING_BLUEPRINT_NAME, __name__)


class PricingAPI(injector.Module):
    @injector.provider
    @flask_injector.request
    def add_item_purchase_price_presenter(self) -> AddingItemPurchasePricePresenter:
        return AddingItemPurchasePricePresenter()

    # @injector.provider
    # @flask_injector.request
    # def add_item_purchase_price_presenter(self) -> AddingItemSellPricePresenter:
    #     return AddingItemSellPricePresenter()
    #
    # @injector.provider
    # @flask_injector.request
    # def add_shop_product_purchase_price_response_boundary(self) -> AddingShopProductPurchasePriceResponseBoundary:
    #     return AddingShopProductPurchasePricePresenter()


@pricing_blueprint.route('/add_purchase_price', methods=['POST'])
@validate_request_timestamp
@jwt_required()
@log_error()
def add_item_purchase_price(add_item_purchase_price_uc: AddItemPurchasePriceUC,
                            presenter: AddingItemPurchasePriceResponseBoundary):
    dto = get_dto(request, AddingItemPurchasePriceRequest, context={'current_user_id': get_jwt_identity()})
    add_item_purchase_price_uc.execute(dto)

    return presenter.response, 201  # type:ignore


@pricing_blueprint.route('/add_sell_price', methods=['POST'])
@validate_request_timestamp
@jwt_required()
@log_error()
def add_item_sell_price(add_item_sell_price_uc: AddItemSellPriceUC, presenter: AddingItemSellPriceResponseBoundary):
    dto = get_dto(request, AddingItemSellPriceRequest, context={'current_user_id': get_jwt_identity()})
    add_item_sell_price_uc.execute(dto)

    return presenter.response, 201  # type:ignore


@pricing_blueprint.route('/add_purchase_price', methods=['POST'])
@jwt_required()
@log_error()
def add_shop_product_purchase_price(add_shop_product_purchase_price_uc: AddShopProductPurchasePriceUC,
                                    presenter: AddingShopProductPurchasePriceResponseBoundary) -> Response:
    dto = get_dto(request, AddingShopProductPurchasePriceRequest, context={'current_user_id': get_jwt_identity()})
    add_shop_product_purchase_price_uc.execute(dto)

    return presenter.response, 201  # type:ignore


@pricing_blueprint.route('/list_purchase_prices', methods=['POST'])
@jwt_required()
@log_error()
def list_shop_product_purchase_prices(
        list_shop_product_purchase_prices_query: ListShopProductPurchasePricesQuery) -> Response:
    dto = get_dto(request, ListShopProductPurchasePricesRequest, context={'current_user_id': get_jwt_identity()})
    prices = list_shop_product_purchase_prices_query.query(dto)

    return make_response(jsonify(prices)), 200  # type:ignore


@pricing_blueprint.route('/get_purchase_price', methods=['POST'])
@jwt_required()
@log_error()
def get_shop_product_purchase_price(
        get_shop_product_purchase_price_query: GetShopProductPurchasePriceQuery) -> Response:
    dto = get_dto(request, GetShopProductPurchasePriceRequest, context={'current_user_id': get_jwt_identity()})
    price = get_shop_product_purchase_price_query.query(dto)

    return make_response(jsonify(price)), 200  # type:ignore


@pricing_blueprint.route('/get_lowest_purchase_price', methods=['POST'])
@jwt_required()
@log_error()
def get_shop_product_lowest_purchase_price(
        get_shop_product_lowest_purchase_price_query: GetShopProductLowestPurchasePriceQuery) -> Response:
    dto = get_dto(request, GetShopProductLowestPurchasePriceRequest, context={'current_user_id': get_jwt_identity()})
    price = get_shop_product_lowest_purchase_price_query.query(dto)

    return make_response(jsonify(price)), 200  # type:ignore
