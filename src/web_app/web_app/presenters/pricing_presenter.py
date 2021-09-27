#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Response, make_response, jsonify

from pricing.services.uc.add_item_purchase_price_uc import AddingItemPurchasePriceResponse, \
    AddingItemPurchasePriceResponseBoundary


class AddingItemPurchasePricePresenter(AddingItemPurchasePriceResponseBoundary):
    response: Response

    def present(self, response_dto: AddingItemPurchasePriceResponse):
        self.response = make_response(jsonify(response_dto.__dict__))
