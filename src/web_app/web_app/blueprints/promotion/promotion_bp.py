#!/usr/bin/env python
# -*- coding: utf-8 -*-
import flask_injector
import injector
from flask import Blueprint, Response, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from promotion.services.usecases.add_product_promotion_uc import AddProductPromotionUC, \
    AddingProductPromotionResponseBoundary, AddingProductPromotionRequest
from web_app.helpers import validate_request_timestamp
from web_app.presenters import log_error
from web_app.serialization.dto import get_dto

PROMOTION_BLUEPRINT_NAME = 'promo_blueprint'
promo_blueprint = Blueprint(PROMOTION_BLUEPRINT_NAME, __name__)


class PromotionAPI(injector.Module):
    @injector.provider
    @flask_injector.request
    def add_product_promotion_resp_bndry(self) -> AddingProductPromotionResponseBoundary:
        return AddingProductPromotionPresenter()


@promo_blueprint.route('/add', method=['POST'])
@validate_request_timestamp
@jwt_required()
@log_error()
def add_product_promotion(add_product_promotion_uc: AddProductPromotionUC,
                          presenter: AddingProductPromotionPresenter) -> Response:
    dto = get_dto(request, AddingProductPromotionRequest, context={'current_user_id': get_jwt_identity()})
    add_product_promotion_uc.execute(dto)

    return presenter.response, 200  # type:ignore
