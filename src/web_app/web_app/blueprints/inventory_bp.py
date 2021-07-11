#!/usr/bin/env python
# -*- coding: utf-8 -*-
import flask_injector
import injector
from flask import Blueprint, Response, request, current_app, make_response, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from foundation.business_rule import BusinessRuleValidationError
from foundation.logger import logger
from inventory import ListProductsBalanceQuery
from inventory.application.inventory_queries import ListDraftPurchaseOrdersQuery
from inventory.application.usecases.approve_purchase_order_uc import ApprovingPurchaseOrderResponseBoundary, \
    ApprovingPurchaseOrderRequest, ApprovePurchaseOrderUC
from inventory.application.usecases.create_draft_purchase_order_uc import CreateDraftPurchaseOrderUC, \
    CreatingDraftPurchaseOrderResponseBoundary, CreatingDraftPurchaseOrderRequest
from inventory.application.usecases.initialize_first_stock_uc import InitializingFirstStockResponseBoundary, \
    InitializeFirstStockUC, InitializingFirstStockRequest
from inventory.application.usecases.remove_draft_purchase_order_item_uc import RemoveDraftPurchaseOrderItemUC, \
    RemovingDraftPurchaseOrderItemResponseBoundary, RemovingDraftPurchaseOrderItemRequest
from inventory.application.usecases.update_draft_purchase_order_uc import UpdateDraftPurchaseOrderUC, \
    UpdatingDraftPurchaseOrderResponseBoundary, UpdatingDraftPurchaseOrderRequest
from web_app.presenters.inventory_presenters import CreatingDraftPurchaseOrderPresenter, \
    RemovingDraftPurchaseOrderItemPresenter, UpdatingDraftPurchaseOrderPresenter, ApprovingPurchaseOrderPresenter
from web_app.serialization.dto import get_dto, AuthorizedPaginationInputDto

INVENTORY_BLUEPRINT_NAME = 'inventory_blueprint'
inventory_blueprint = Blueprint(INVENTORY_BLUEPRINT_NAME, __name__)


class InventoryAPI(injector.Module):
    @injector.provider
    @flask_injector.request
    def creating_draft_purchase_order_boundary(self) -> CreatingDraftPurchaseOrderResponseBoundary:
        return CreatingDraftPurchaseOrderPresenter()

    @injector.provider
    @flask_injector.request
    def removing_draft_purchase_order_item_boundary(self) -> RemovingDraftPurchaseOrderItemResponseBoundary:
        return RemovingDraftPurchaseOrderItemPresenter()

    @injector.provider
    @flask_injector.request
    def updating_draft_purchase_order_response_boundary(self) -> UpdatingDraftPurchaseOrderResponseBoundary:
        return UpdatingDraftPurchaseOrderPresenter()

    @injector.provider
    @flask_injector.request
    def approving_purchase_order_response_boundary(self) -> ApprovingPurchaseOrderResponseBoundary:
        return ApprovingPurchaseOrderPresenter()


@inventory_blueprint.route('/', methods=['GET'])
@jwt_required()
def list_products_balance(list_products_balance_query: ListProductsBalanceQuery) -> Response:
    try:
        current_user = get_jwt_identity()
        dto = get_dto(request, AuthorizedPaginationInputDto, context={'current_user': current_user})
        response = list_products_balance_query.query(dto)
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


@inventory_blueprint.route('/purchase_order', methods=['GET'])
@jwt_required()
def list_draft_purchase_orders(list_draft_purchase_orders_query: ListDraftPurchaseOrdersQuery) -> Response:
    try:
        current_user = get_jwt_identity()
        dto = get_dto(request, AuthorizedPaginationInputDto, context={'current_user': current_user})
        response = list_draft_purchase_orders_query.query(dto)
        return make_response(jsonify(response)), 200  # type:ignore
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
def add_draft_purchase_order_item(update_draft_purchase_order_uc: UpdateDraftPurchaseOrderUC,
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


@inventory_blueprint.route('/purchase_order/item', methods=['DELETE'])
@jwt_required()
def remove_draft_purchase_order_item(remove_draft_purchase_order_item_uc: RemoveDraftPurchaseOrderItemUC,
                                     presenter: RemovingDraftPurchaseOrderItemResponseBoundary) -> Response:
    try:
        dto = get_dto(request, RemovingDraftPurchaseOrderItemRequest, context={
            'current_user': get_jwt_identity()
        })
        remove_draft_purchase_order_item_uc.execute(dto)
        return presenter.response, 200  # type:ignore
    except BusinessRuleValidationError as exc:
        return make_response(jsonify({'message': exc.details})), 400  # type: ignore
    except Exception as exc:
        if current_app.debug:
            logger.exception(exc)
        return make_response(jsonify({'message': exc.args})), 400  # type:ignore


@inventory_blueprint.route('/purchase_order/<draft_purchase_order_id>', methods=['POST'])
@jwt_required()
def approve_purchase_order(draft_purchase_order_id: str,
                           approve_purchase_order_uc: ApprovePurchaseOrderUC,
                           presenter: ApprovingPurchaseOrderResponseBoundary) -> Response:
    try:
        dto = get_dto(request, ApprovingPurchaseOrderRequest, context={
            'draft_purchase_order_id': draft_purchase_order_id,
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
