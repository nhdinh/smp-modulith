#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector
from flask import Blueprint, Response, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from foundation.business_rule import BusinessRuleValidationError
from foundation.logger import logger
from inventory.application.usecases.initialize_first_stock_uc import InitializingFirstStockResponseBoundary, \
    InitializeFirstStockUC, InitializingFirstStockRequest
from web_app.serialization.dto import get_dto

INVENTORY_BLUEPRINT_NAME = 'inventory_blueprint'
inventory_blueprint = Blueprint(INVENTORY_BLUEPRINT_NAME, __name__)


class InventoryAPI(injector.Module):
    ...


@inventory_blueprint.route('/first_stock', methods=['PUT'])
@jwt_required()
def first_stock(first_stock_uc: InitializeFirstStockUC, presenter: InitializingFirstStockResponseBoundary) -> Response:
    try:
        current_user = get_jwt_identity()
        dto = get_dto(request, InitializingFirstStockRequest, context={'current_user': current_user})
        first_stock_uc.execute(dto)

        return presenter.response, 201  # type:ignore
    except BusinessRuleValidationError as exc:
        return make_response(jsonify({'message': exc.details})), 400  # type: ignore
    except Exception as exc:
        if current_app.debug:
            logger.exception(exc)
        return make_response(jsonify({'message': exc.args})), 400  # type:ignore
