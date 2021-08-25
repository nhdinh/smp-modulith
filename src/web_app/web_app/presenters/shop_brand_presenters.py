#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Response, make_response, jsonify

from shop.application.usecases.brand.set_shop_brands_status_uc import SettingShopBrandsStatusResponseBoundary, \
    SettingShopBrandsStatusResponse
from shop.application.usecases.brand.update_shop_brand_uc import UpdatingShopBrandResponseBoundary, \
    UpdatingShopBrandResponse


class SettingShopBrandsStatusPresenter(SettingShopBrandsStatusResponseBoundary):
    response: Response

    def present(self, response_dto: SettingShopBrandsStatusResponse):
        self.response = make_response(jsonify(response_dto.__dict__))


class UpdatingShopBrandPresenter(UpdatingShopBrandResponseBoundary):
    response: Response

    def present(self, response_dto: UpdatingShopBrandResponse):
        self.response = make_response(jsonify(response_dto.__dict__))
