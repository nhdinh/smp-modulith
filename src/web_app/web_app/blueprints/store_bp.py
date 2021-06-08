#!/usr/bin/env python
# -*- coding: utf-8 -*-
import flask_injector
import injector
from flask import Blueprint, Response, request, current_app, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity

from foundation.business_rule import BusinessRuleValidationError
from store.application.usecases.add_store_manager import AddingStoreManagerResponseBoundary, AddingStoreManagerResponse, \
    AddStoreManagerUC
from store.application.usecases.choose_store_plan_uc import ChooseStorePlanUC, ChoosenStorePlanResponseBoundary, \
    ChoosenStorePlanRequest, ChoosenStorePlanResponse
from store.application.usecases.confirm_store_registration_uc import ConfirmStoreRegistrationUC, \
    ConfirmingStoreRegistrationResponseBoundary, ConfirmingStoreRegistrationRequest, ConfirmingStoreRegistrationResponse
from store.application.store_queries import FetchStoreSettingsQuery
from store.application.usecases.register_store_uc import RegisterStoreUC, RegisteringStoreResponseBoundary, \
    RegisteringStoreRequest, RegisteringStoreResponse
from store.application.usecases.update_store_settings_uc import UpdatingStoreSettingsResponseBoundary, \
    UpdatingStoreSettingsRequest, UpdateStoreSettingsUC, UpdatingStoreSettingsResponse
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

    @injector.provider
    @flask_injector.request
    def choose_store_plan_boundary(self) -> ChoosenStorePlanResponseBoundary:
        return ChoosenStorePlanPresenter()

    @injector.provider
    @flask_injector.request
    def add_store_manager_boundary(self) -> AddingStoreManagerResponseBoundary:
        return AddingStoreManagerPresenter()

    @injector.provider
    @flask_injector.request
    def update_store_settings_boundary(self) -> UpdatingStoreSettingsResponseBoundary:
        return UpdatingStoreSettingsPresenter()


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


def confirm_store_registration(confirmation_token, confirm_store_registration_uc: ConfirmStoreRegistrationUC,
                               presenter: ConfirmingStoreRegistrationResponseBoundary) -> Response:
    try:
        confirm_store_registration_uc.execute(confirmation_token)
        return presenter.response, 201  # type: ignore
    except BusinessRuleValidationError as exc:
        return make_response(jsonify({'message': exc.details})), 400  # type: ignore
    except Exception as exc:
        if current_app.debug:
            raise exc
        return make_response(jsonify({'messages': exc.args})), 400  # type: ignore


@store_blueprint.route('/confirm', methods=['POST'])
def confirm_store_registration_post(confirm_store_registration_uc: ConfirmStoreRegistrationUC,
                                    presenter: ConfirmingStoreRegistrationResponseBoundary) -> Response:
    try:
        dto = get_dto(request, ConfirmingStoreRegistrationRequest, context={})
        return confirm_store_registration(dto.confirmation_token, confirm_store_registration_uc, presenter)
    except Exception as exc:
        return make_response(jsonify({'messages': exc.args})), 400  # type: ignore


@store_blueprint.route('/confirm/<string:confirmation_token>', methods=['GET'])
def confirm_store_registration_get(confirmation_token: str, confirm_store_registration_uc: ConfirmStoreRegistrationUC,
                                   presenter: ConfirmingStoreRegistrationResponseBoundary) -> Response:
    try:
        return confirm_store_registration(confirmation_token, confirm_store_registration_uc, presenter)
    except Exception as exc:
        return make_response(jsonify({'messages': exc.args})), 400  # type: ignore


@store_blueprint.route('/choose', methods=['POST'])
@jwt_required()
def confirm_store_package(choose_store_plan_uc: ChooseStorePlanUC,
                          presenter: ChoosenStorePlanResponseBoundary) -> Response:
    try:
        store_owner = get_jwt_identity()
        dto = get_dto(request, ChoosenStorePlanRequest, context={'store_owner': store_owner})
        choose_store_plan_uc.execute(dto)
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


@store_blueprint.route('/managers/', methods=['GET'])
@jwt_required()
def fetch_store_managers() -> Response:
    return None


@store_blueprint.route('/managers/add', methods=['POST'])
@jwt_required()
def add_store_manager(add_store_manager_uc: AddStoreManagerUC,
                      presenter: AddingStoreManagerResponseBoundary) -> Response:
    raise NotImplementedError


@store_blueprint.route('/managers/<string:login>', methods=['PATCH'])
@jwt_required()
def patch_store_manager(login: str) -> Response:
    raise NotImplementedError


class RegisteringStorePresenter(RegisteringStoreResponseBoundary):
    response: Response

    def present(self, response_dto: RegisteringStoreResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))


class ConfirmingStoreRegistrationPresenter(ConfirmingStoreRegistrationResponseBoundary):
    response: Response

    def present(self, response_dto: ConfirmingStoreRegistrationResponse):
        self.response = make_response(jsonify(response_dto.__dict__))


class ChoosenStorePlanPresenter(ChoosenStorePlanResponseBoundary):
    response: Response

    def present(self, response_dto: ChoosenStorePlanResponse):
        self.response = make_response(jsonify(response_dto.__dict__))


class AddingStoreManagerPresenter(AddingStoreManagerResponseBoundary):
    response: Response

    def present(self, response_dto: AddingStoreManagerResponse):
        self.response = make_response(jsonify(response_dto.__dict__))


class UpdatingStoreSettingsPresenter(UpdatingStoreSettingsResponseBoundary):
    response: Response

    def present(self, response_dto: UpdatingStoreSettingsResponse):
        self.response = make_response(jsonify(response_dto.__dict__))
