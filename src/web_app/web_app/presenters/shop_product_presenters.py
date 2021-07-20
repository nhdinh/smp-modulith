#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import jsonify, make_response

from payments.api.responses import Response
from shop.application.usecases.product.add_shop_product_unit_uc import (
    AddingShopProductUnitResponse,
    AddingShopProductUnitResponseBoundary,
)
from shop.application.usecases.product.update_shop_product_unit_uc import (
    UpdatingShopProductUnitResponse,
    UpdatingShopProductUnitResponseBoundary,
)


class AddingShopProductUnitPresenter(AddingShopProductUnitResponseBoundary):
    response: Response

    def present(self, response_dto: AddingShopProductUnitResponse):
        self.response = make_response(jsonify(response_dto.__dict__))


class UpdatingShopProductUnitPresenter(UpdatingShopProductUnitResponseBoundary):
    response: Response

    def present(self, response_dto: UpdatingShopProductUnitResponse):
        self.response = make_response(jsonify(response_dto.__dict__))
