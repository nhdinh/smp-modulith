#!/usr/bin/env python
# -*- coding: utf-8 -*-
import flask_injector
import injector
from flask import Blueprint, Response, request, current_app, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity

from foundation.business_rule import BusinessRuleValidationError
from product_catalog.application.usecases.confirm_store_registration import ConfirmStoreRegistrationUC, \
    ConfirmingStoreRegistrationResponseBoundary, ConfirmingStoreRegistrationRequest, ConfirmingStoreRegistrationResponse
from store.application.store_queries import FetchStoreSettingsQuery
from store.application.usecases.register_store_uc import RegisterStoreUC, RegisteringStoreResponseBoundary, \
    RegisteringStoreRequest, RegisteringStoreResponse
from store.application.usecases.update_store_settings_uc import UpdatingStoreSettingsResponseBoundary, \
    UpdatingStoreSettingsRequest, UpdateStoreSettingsUC
from web_app.serialization.dto import get_dto

store_blueprint = Blueprint('store_blueprint', __name__)


class StoreAPI(injector.Module):
    @injector.provider
    @flask_injector.request
    def register_store_response_boundary(self) -> RegisteringStoreResponseBoundary:
        return RegisteringStorePresenter()

    @injector.provider
    @flask_injector.request
    def confirm_store_registration_boundary(self) -> ConfirmingStoreRegistrationResponseBoundary:
        return ConfirmingStoreRegistrationPresenter()


@store_blueprint.route('/register', methods=['POST'])
def register_new_store(register_store_uc: RegisterStoreUC, presenter: RegisteringStoreResponseBoundary) -> Response:
    try:
        dto = get_dto(request, RegisteringStoreRequest, context={})
        register_store_uc.execute(dto)
        return presenter.response, 201  # type: ignore
    except BusinessRuleValidationError as exc:
        return make_response(jsonify({'message': exc.details})), 400  # type: ignore
    except Exception as exc:
        if current_app.debug:
            raise exc
        return make_response(jsonify({'messages': exc.args})), 400  # type: ignore


@store_blueprint.route('/confirm', methods=['POST'])
def confirm_store_registration(confirm_store_registration_uc: ConfirmStoreRegistrationUC,
                               presenter: ConfirmingStoreRegistrationResponseBoundary) -> Response:
    try:
        dto = get_dto(request, ConfirmingStoreRegistrationRequest, context={})
        confirm_store_registration_uc.execute(dto)
        return presenter.response, 201  # type: ignore
    except BusinessRuleValidationError as exc:
        return make_response(jsonify({'message': exc.details})), 400  # type: ignore
    except Exception as exc:
        if current_app.debug:
            raise exc
        return make_response(jsonify({'messages': exc.args})), 400  # type: ignore


@store_blueprint.route('/settings', methods=['GET'])
@jwt_required()
def fetch_store_settings(query: FetchStoreSettingsQuery) -> Response:
    try:
        store_owner = get_jwt_identity()
        settings = query.query(store_of=store_owner)
        return make_response(jsonify(settings)), 200  # type:ignore
    except Exception as exc:
        if current_app.debug:
            raise exc
        return make_response(jsonify({'messages': exc.args})), 400  # type: ignore


@store_blueprint.route('/settings', methods=['PATCH'])
@jwt_required()
def update_store_settings(update_store_settings_uc: UpdateStoreSettingsUC,
                          presenter: UpdatingStoreSettingsResponseBoundary):
    try:
        dto = get_dto(request, UpdatingStoreSettingsRequest, context={})
        update_store_settings_uc.execute(dto)
        return presenter.response, 201  # type: ignore
    except BusinessRuleValidationError as exc:
        return make_response(jsonify({'message': exc.details})), 400  # type: ignore
    except Exception as exc:
        if current_app.debug:
            raise exc
        return make_response(jsonify({'messages': exc.args})), 400  # type: ignore


class RegisteringStorePresenter(RegisteringStoreResponseBoundary):
    response: Response

    def present(self, response_dto: RegisteringStoreResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))


class ConfirmingStoreRegistrationPresenter(ConfirmingStoreRegistrationResponseBoundary):
    response: Response

    def present(self, response_dto: ConfirmingStoreRegistrationResponse):
        self.response = make_response(jsonify(response_dto.__dict__))
