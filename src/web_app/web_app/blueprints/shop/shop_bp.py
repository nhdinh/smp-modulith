#!/usr/bin/env python
# -*- coding: utf-8 -*-
import flask_injector
import injector
from flask import Blueprint, Response, request, make_response, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from shop.application.queries.shop_queries import ListShopAddressesQuery, ListShopAddressesRequest
from shop.application.usecases.initialize.confirm_shop_registration_uc import (
    ConfirmingShopRegistrationRequest,
    ConfirmingShopRegistrationResponseBoundary,
    ConfirmShopRegistrationUC,
)
from shop.application.usecases.initialize.register_shop_uc import (
    RegisteringShopRequest,
    RegisteringShopResponseBoundary,
    RegisterShopUC,
)
from shop.application.usecases.shop.add_shop_address_uc import AddingShopAddressResponseBoundary, AddShopAddressUC, \
    AddingShopAddressRequest
from web_app.presenters import log_error
from web_app.presenters.shop_presenters import RegisteringShopPresenter
from web_app.presenters.store_management_presenters import ConfirmingShopRegistrationPresenter, \
    AddingShopAddressPresenter
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
    def confirm_shop_registration_response_boundary(self) -> ConfirmingShopRegistrationResponseBoundary:
        return ConfirmingShopRegistrationPresenter()

    @injector.provider
    @flask_injector.request
    def add_shop_address_response_boundary(self) -> AddingShopAddressResponseBoundary:
        return AddingShopAddressPresenter()


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


@shop_blueprint.route('/list_addresses', methods=['GET', 'POST'])
@jwt_required()
@log_error()
def list_shop_addresses(list_shop_addresses_query: ListShopAddressesQuery) -> Response:
    dto = get_dto(request, ListShopAddressesRequest, context={'partner_id': get_jwt_identity()})
    addresses = list_shop_addresses_query.query(dto)

    return make_response(jsonify(addresses)), 200  # type:ignore


@shop_blueprint.route('/add_address', methods=['POST'])
@jwt_required()
@log_error()
def add_shop_address(add_shop_address_uc: AddShopAddressUC, presenter: AddingShopAddressResponseBoundary) -> Response:
    dto = get_dto(request, AddingShopAddressRequest, context={'partner_id': get_jwt_identity()})
    add_shop_address_uc.execute(dto)

    return presenter.response, 201  # type: ignore
