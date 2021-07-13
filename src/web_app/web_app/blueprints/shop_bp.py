#!/usr/bin/env python
# -*- coding: utf-8 -*-
import flask_injector
import injector
from flask import Blueprint, request, current_app, Response, make_response, jsonify

from foundation.business_rule import BusinessRuleValidationError
from foundation.logger import logger
from store import RegisterShopUC, RegisteringShopResponseBoundary
from store.application.usecases.initialize.register_shop_uc import RegisteringShopRequest
from web_app.presenters.shop_presenters import RegisteringShopPresenter
from web_app.serialization.dto import get_dto

SHOP_BLUEPRINT_NAME = 'shop_blueprint'
shop_blueprint = Blueprint(SHOP_BLUEPRINT_NAME, __name__)


class ShopAPI(injector.Module):
    @injector.provider
    @flask_injector.request
    def register_shop_response_boundary(self) -> RegisteringShopResponseBoundary:
        return RegisteringShopPresenter()


@shop_blueprint.route('/register', methods=['POST'])
def register_new_store(register_shop_uc: RegisterShopUC, presenter: RegisteringShopResponseBoundary) -> Response:
    try:
        dto = get_dto(request, RegisteringShopRequest, context={})
        register_shop_uc.execute(dto)
        return presenter.response, 201  # type: ignore
    except BusinessRuleValidationError as exc:
        return make_response(jsonify({'message': exc.details})), 422  # type: ignore
    except Exception as exc:
        if current_app.debug:
            logger.exception(exc)
        return make_response(jsonify({'messages': exc.args})), 400  # type: ignore
