#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Response, make_response, jsonify
from inventory.application.usecases.approve_purchase_order_uc import ApprovingPurchaseOrderResponseBoundary, \
    ApprovingPurchaseOrderResponse

from inventory.application.usecases.create_draft_purchase_order_uc import CreatingDraftPurchaseOrderResponseBoundary, \
    CreatingDraftPurchaseOrderResponse
from inventory.application.usecases.remove_draft_purchase_order_item_uc import \
    RemovingDraftPurchaseOrderItemResponseBoundary, RemovingDraftPurchaseOrderItemResponse
from inventory.application.usecases.update_draft_purchase_order_uc import UpdatingDraftPurchaseOrderResponse, \
    UpdatingDraftPurchaseOrderResponseBoundary


class CreatingDraftPurchaseOrderPresenter(CreatingDraftPurchaseOrderResponseBoundary):
    response: Response

    def present(self, response_dto: CreatingDraftPurchaseOrderResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))


class RemovingDraftPurchaseOrderItemPresenter(RemovingDraftPurchaseOrderItemResponseBoundary):
    response: Response

    def present(self, response_dto: RemovingDraftPurchaseOrderItemResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))


class UpdatingDraftPurchaseOrderPresenter(UpdatingDraftPurchaseOrderResponseBoundary):
    response: Response

    def present(self, response_dto: UpdatingDraftPurchaseOrderResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))


class ApprovingPurchaseOrderPresenter(ApprovingPurchaseOrderResponseBoundary):
    response: Response

    def present(self, response_dto: ApprovingPurchaseOrderResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))
