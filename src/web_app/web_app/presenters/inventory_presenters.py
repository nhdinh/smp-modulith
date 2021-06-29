#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Response, make_response, jsonify

from inventory.application.usecases.create_draft_purchase_order_uc import CreatingDraftPurchaseOrderResponseBoundary, \
    CreatingDraftPurchaseOrderResponse


class CreatingDraftPurchaseOrderPresenter(CreatingDraftPurchaseOrderResponseBoundary):
    response: Response

    def present(self, response_dto: CreatingDraftPurchaseOrderResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))
