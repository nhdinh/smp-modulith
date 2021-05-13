#!/usr/bin/env python
# -*- coding: utf-8 -*-
import flask_injector
import injector
from flask import Blueprint, Response, make_response, jsonify, request, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

from auth.application.queries.identity import GetAllUsersQuery, GetSingleUserQuery
from auth.application.usecases.log_user_in import LoggingUserInUC, LoggingUserInResponseBoundary, LoggedUserResponse, \
    LoggingUserInRequest
from auth.application.usecases.register_user import RegisteringUserUC, RegisteringUserResponseBoundary, \
    RegisteringUserRequest, RegisteringUserResponse
from foundation.business_rule import BusinessRuleValidationError
from web_app.serialization.dto import get_dto

auth_blueprint = Blueprint('auth_blueprint', __name__)


class AuthenticationAPI(injector.Module):
    @injector.provider
    @flask_injector.request
    def register_user_response_boundary(self) -> RegisteringUserResponseBoundary:
        return RegisteringUserPresenter()

    @injector.provider
    @flask_injector.request
    def log_user_in_response_boundary(self) -> LoggingUserInResponseBoundary:
        return LoggingUserInPresenter()


@auth_blueprint.route('/register', methods=['POST'], strict_slashes=False)
def register_user(registering_user_uc: RegisteringUserUC, presenter: RegisteringUserResponseBoundary):
    try:
        dto = get_dto(request, RegisteringUserRequest, context={})
        registering_user_uc.execute(dto)

        return presenter.response, 201  # type: ignore
    except BusinessRuleValidationError as exc:
        return make_response(jsonify({'message': exc.details})), 400  # type:ignore
    except Exception as exc:
        if current_app.debug:
            raise exc

        return make_response(jsonify({'messages': exc.args})), 400  # type:ignore


@auth_blueprint.route('/login', methods=['POST'])
def user_login(logging_user_in_uc: LoggingUserInUC, presenter: LoggingUserInResponseBoundary) -> Response:
    try:
        dto = get_dto(request, LoggingUserInRequest, context={})
        logging_user_in_uc.execute(dto)

        return presenter.response, 200  # type:ignore
    except Exception as exc:
        if current_app.debug:
            raise exc

        return make_response(jsonify({'messages': exc.args})), 400  # type:ignore


@auth_blueprint.route('/logout', methods=['POST'])
@jwt_required()
def user_logout():
    pass


@auth_blueprint.route('/refresh-token', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)

    return make_response(jsonify({'access_token': access_token})), 200


@auth_blueprint.route('/', methods=['POST'])
def list_all_users(query: GetAllUsersQuery) -> Response:
    return make_response(jsonify(query.query()))


@auth_blueprint.route('/current', methods=['GET'])
def get_current_user(query: GetSingleUserQuery) -> Response:
    return make_response(jsonify(query.query()))


@auth_blueprint.route('/', methods=['DELETE'])
def delete_user():
    pass


class RegisteringUserPresenter(RegisteringUserResponseBoundary):
    response: Response

    def present(self, response_dto: RegisteringUserResponse) -> None:
        access_token = create_access_token(identity=response_dto.email)
        refresh_token = create_refresh_token(identity=response_dto.email)

        # update response_dto with access_token and refresh_token
        response_dto = _merge_dict(
            response_dto.__dict__,
            {
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        )
        self.response = make_response(jsonify(response_dto))


class LoggingUserInPresenter(LoggingUserInResponseBoundary):
    response: Response

    def present(self, response_dto: LoggedUserResponse) -> None:
        access_token = create_access_token(identity=response_dto.username)
        refresh_token = create_refresh_token(identity=response_dto.username)

        # update response_dto with access_token and refresh_token
        response_dto = _merge_dict(
            response_dto.__dict__,
            {
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        )
        self.response = make_response(jsonify(response_dto))


def _merge_dict(dict1, dict2):
    dict1.update(dict2)
    return dict1
