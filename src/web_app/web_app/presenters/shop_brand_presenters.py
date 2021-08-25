#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Response, make_response, jsonify

from shop.application.usecases.brand.set_shop_brands_status_uc import SettingShopBrandsStatusResponseBoundary, \
    SettingShopBrandsStatusResponse


class SettingShopBrandsStatusPresenter(SettingShopBrandsStatusResponseBoundary):
    response: Response

    def present(self, response_dto: SettingShopBrandsStatusResponse):
        self.response = make_response(jsonify(response_dto.__dict__))
