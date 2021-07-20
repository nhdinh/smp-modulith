#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from flask import Response, jsonify, make_response

from shop.application.usecases.initialize.register_shop_uc import (
    RegisteringShopResponse,
    RegisteringShopResponseBoundary,
)
from shop.domain.entities.value_objects import RegistrationStatus


@dataclass
class RegistrationStatusDto:
    registration_status: RegistrationStatus

    def serialize(self):
        return self.registration_status.value


class RegisteringShopPresenter(RegisteringShopResponseBoundary):
    response: Response

    def present(self, response_dto: RegisteringShopResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))
