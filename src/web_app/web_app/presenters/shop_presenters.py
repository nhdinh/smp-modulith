#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Response, make_response, jsonify

from store.application.usecases.initialize.register_shop_uc import RegisteringStoreResponse, \
    RegisteringShopResponseBoundary


class RegisteringShopPresenter(RegisteringShopResponseBoundary):
    response: Response

    def present(self, response_dto: RegisteringStoreResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))