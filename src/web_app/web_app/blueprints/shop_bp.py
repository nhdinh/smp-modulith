#!/usr/bin/env python
# -*- coding: utf-8 -*-
import flask_injector
import injector
from flask import Blueprint, request, Response

from shop.application.usecases.initialize.confirm_shop_registration_uc import ConfirmShopRegistrationUC, \
    ConfirmingShopRegistrationResponseBoundary, ConfirmingShopRegistrationRequest
from shop.application.usecases.initialize.register_shop_uc import RegisteringShopResponseBoundary, RegisterShopUC, \
    RegisteringShopRequest
from web_app.presenters import log_error
from web_app.presenters.shop_presenters import RegisteringShopPresenter
from web_app.presenters.store_management_presenters import ConfirmingShopRegistrationPresenter
from web_app.serialization.dto import get_dto

SHOP_BLUEPRINT_NAME = 'shop_blueprint'
shop_blueprint = Blueprint(SHOP_BLUEPRINT_NAME, __name__)


class ShopAPI(injector.Module):
    @injector.provider
    @flask_injector.request
    def register_shop_response_boundary(self) -> RegisteringShopResponseBoundary:
        return RegisteringShopPresenter()

    @injector.provider
    @flask_injector.request
    def confirm_sho_registration_response_boundary(self) -> ConfirmingShopRegistrationResponseBoundary:
        return ConfirmingShopRegistrationPresenter()


@shop_blueprint.route('/register', methods=['POST'])
@log_error()
def register_new_shop(register_shop_uc: RegisterShopUC, presenter: RegisteringShopResponseBoundary) -> Response:
    # try:
    dto = get_dto(request, RegisteringShopRequest, context={})
    register_shop_uc.execute(dto)
    return presenter.response, 201  # type: ignore


@shop_blueprint.route('/confirm', methods=['POST'])
@log_error()
def confirm_registration(confirm_registration_uc: ConfirmShopRegistrationUC,
                         presenter: ConfirmingShopRegistrationResponseBoundary) -> Response:
    dto = get_dto(request, ConfirmingShopRegistrationRequest, context={})
    confirm_registration_uc.execute(dto)
    return presenter.response, 201  # type: ignore
