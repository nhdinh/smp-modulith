#!/usr/bin/env python
# -*- coding: utf-8 -*-
import flask_injector
import injector
from flask import Blueprint, Response, request, current_app, make_response, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from inventory import FetchAllProductsBalanceQuery
from inventory.application.usecases.approve_purchase_order_uc import ApprovingPurchaseOrderResponseBoundary, \
    ApprovingPurchaseOrderRequest, ApprovePurchaseOrderUC
from inventory.application.usecases.create_draft_purchase_order_uc import CreateDraftPurchaseOrderUC, \
    CreatingDraftPurchaseOrderResponseBoundary, CreatingDraftPurchaseOrderRequest

from foundation.business_rule import BusinessRuleValidationError
from foundation.logger import logger
from inventory.application.usecases.initialize_first_stock_uc import InitializingFirstStockResponseBoundary, \
    InitializeFirstStockUC, InitializingFirstStockRequest
from inventory.application.usecases.update_draft_purchase_order_uc import UpdateDraftPurchaseOrderUC, \
    UpdatingDraftPurchaseOrderResponseBoundary, UpdatingDraftPurchaseOrderRequest
from web_app.presenters.inventory_presenters import CreatingDraftPurchaseOrderPresenter
from web_app.serialization.dto import get_dto, AuthorizedPaginationInputDto

INVENTORY_BLUEPRINT_NAME = 'inventory_blueprint'
inventory_blueprint = Blueprint(INVENTORY_BLUEPRINT_NAME, __name__)


class InventoryAPI(injector.Module):
    @injector.provider
    @flask_injector.request
    def creating_draft_purchase_order_boundary(self) -> CreatingDraftPurchaseOrderResponseBoundary:
        return CreatingDraftPurchaseOrderPresenter()

@inventory_blueprint.route('/', methods=['GET'])
@jwt_required()
def fetch_products_balance(fetch_all_products_balance_query: FetchAllProductsBalanceQuery)->Response:
    try:
        current_user = get_jwt_identity()
        dto = get_dto(request, AuthorizedPaginationInputDto, context={'current_user': current_user})
        response = fetch_all_products_balance_query.query(dto)
        return make_response(jsonify(response)), 200  # type:ignore
    except Exception as exc:
        if current_app.debug:
            logger.exception(exc)
        return make_response(jsonify({'message': exc.args})), 400  # type:ignore


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


@inventory_blueprint.route('/purchase_order', methods=['POST'])
@jwt_required()
def create_draft_purchase_order(create_draft_purchase_order_uc: CreateDraftPurchaseOrderUC,
                                presenter: CreatingDraftPurchaseOrderResponseBoundary) -> Response:
    try:
        dto = get_dto(request, CreatingDraftPurchaseOrderRequest, context={
            'current_user': get_jwt_identity()
        })
        create_draft_purchase_order_uc.execute(dto)
        return presenter.response, 201  # type:ignore
    except BusinessRuleValidationError as exc:
        return make_response(jsonify({'message': exc.details})), 400  # type: ignore
    except Exception as exc:
        if current_app.debug:
            logger.exception(exc)
        return make_response(jsonify({'message': exc.args})), 400  # type:ignore


@inventory_blueprint.route('/purchase_order', methods=['PATCH'])
@jwt_required()
def add_purchase_order_item(update_draft_purchase_order_uc: UpdateDraftPurchaseOrderUC,
                            presenter: UpdatingDraftPurchaseOrderResponseBoundary) -> Response:
    try:
        dto = get_dto(request, UpdatingDraftPurchaseOrderRequest, context={
            'current_user': get_jwt_identity()
        })
        update_draft_purchase_order_uc.execute(dto)
        return presenter.response, 200  # type:ignore
    except BusinessRuleValidationError as exc:
        return make_response(jsonify({'message': exc.details})), 400  # type: ignore
    except Exception as exc:
        if current_app.debug:
            logger.exception(exc)
        return make_response(jsonify({'message': exc.args})), 400  # type:ignore


@inventory_blueprint.route('/purchase_order/<string:purchase_order_id>', methods=['PATCH'])
@jwt_required()
def approve_purchase_order(purchase_order_id: str,
                           approve_purchase_order_uc: ApprovePurchaseOrderUC,
                           presenter: ApprovingPurchaseOrderResponseBoundary) -> Response:
    try:
        dto = get_dto(request, ApprovingPurchaseOrderRequest, context={
            'purchase_order_id': purchase_order_id,
            'current_user': get_jwt_identity()
        })
        approve_purchase_order_uc.execute(dto)
        return presenter.response, 200  # type:ignore
    except BusinessRuleValidationError as exc:
        return make_response(jsonify({'message': exc.details})), 400  # type: ignore
    except Exception as exc:
        if current_app.debug:
            logger.exception(exc)
        return make_response(jsonify({'message': exc.args})), 400  # type:ignore
