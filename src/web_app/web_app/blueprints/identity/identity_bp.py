#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Union

import flask_injector
import injector
from flask import Blueprint, Response, current_app, jsonify, make_response, request
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt, get_jwt_identity, jwt_required

from foundation.logger import logger
from identity.application.queries.identity_sql_queries import GetAllUsersQuery, GetSingleUserQuery, \
    GetSingleUserRequest, GetCurrentUserRequest
from identity.application.usecases.change_password_uc import (
    ChangePasswordUC,
    ChangingPasswordRequest,
    ChangingPasswordResponse,
    ChangingPasswordResponseBoundary,
    ResettingPasswordRequest,
)
from identity.application.usecases.log_user_in_uc import (
    LoggedUserResponse,
    LoggingUserInRequest,
    LoggingUserInResponseBoundary,
    LoggingUserInUC, FailedLoginResponse,
)
from identity.application.usecases.register_user_uc import (
    RegisteringAccountRequest,
    RegisteringUserResponse,
    RegisteringAccountResponseBoundary,
    RegisterAccountUC,
)
from identity.application.usecases.request_to_change_password_uc import (
    RequestingToChangePasswordRequest,
    RequestingToChangePasswordResponse,
    RequestingToChangePasswordResponseBoundary,
    RequestToChangePasswordUC,
)
from identity.application.usecases.revoke_token_uc import RevokingTokenUC
from identity.domain.entities.revoked_token import RevokedToken
from web_app.presenters import log_error
from web_app.serialization.dto import get_dto

IDENTITY_BLUEPRINT_NAME = 'identity_blueprint'
identity_blueprint = Blueprint(IDENTITY_BLUEPRINT_NAME, __name__)


class IdentityAPI(injector.Module):
    @injector.provider
    @flask_injector.request
    def register_account_response_boundary(self) -> RegisteringAccountResponseBoundary:
        return RegisteringAccountPresenter()

    @injector.provider
    @flask_injector.request
    def log_user_in_response_boundary(self) -> LoggingUserInResponseBoundary:
        return LoggingUserInPresenter()

    @injector.provider
    @flask_injector.request
    def request_to_change_password_response_boundary(self) -> RequestingToChangePasswordResponseBoundary:
        return RequestingToChangePasswordPresenter()

    @injector.provider
    @flask_injector.request
    def change_password_response_boundary(self) -> ChangingPasswordResponseBoundary:
        return ChangingPasswordPresenter()


@identity_blueprint.route('/register', methods=['POST'], strict_slashes=False)
@log_error()
def register_user(registering_account_uc: RegisterAccountUC, presenter: RegisteringAccountResponseBoundary):
    """
    Register a new user account

    :param registering_account_uc: The usecase processor named RegisteringUser
    :param presenter: the output present formatter
    :return:
    """
    # try:
    dto = get_dto(request, RegisteringAccountRequest, context={})
    registering_account_uc.execute(dto)

    return presenter.response, 201  # type: ignore


@identity_blueprint.route('/login', methods=['POST'])
@log_error()
def user_login(logging_user_in_uc: LoggingUserInUC, presenter: LoggingUserInResponseBoundary) -> Response:
    # UserLogin
    dto = get_dto(request, LoggingUserInRequest, context={
        'current_ip': request.remote_addr
    })
    logging_user_in_uc.execute(dto)

    return presenter.response, presenter.response.status  # type:ignore


@identity_blueprint.route('/logout', methods=['POST'])
@jwt_required()
def user_logout_access(revoking_token_uc: RevokingTokenUC):
    jti = get_jwt()['jti']
    try:
        revoked_token = RevokedToken(jti=jti)
        revoking_token_uc.execute(revoked_token)

        return make_response(jsonify({'message': 'Access token has been revoked'}))
    except Exception as exc:
        return make_response(jsonify({'message': 'Something wrong'})), 500


@identity_blueprint.route('/logout/refresh', methods=['POST'])
@jwt_required(refresh=True)
def user_logout_refresh(revoking_token_uc: RevokingTokenUC):
    jti = get_jwt()['jti']
    try:
        revoked_token = RevokedToken(jti=jti)
        revoking_token_uc.execute(revoked_token)

        return make_response(jsonify({'message': 'Refresh token has been revoked'}))
    except Exception as exc:
        if current_app.debug:
            logger.exception(exc)

        return make_response(jsonify({'message': 'Something wrong'})), 500


@identity_blueprint.route('/refresh-token', methods=['POST'])
@jwt_required(refresh=True)
@log_error()
def refresh_token(query: GetSingleUserQuery):
    # TokenRefresh
    dto = get_dto(request, GetCurrentUserRequest, context={'current_user_id': get_jwt_identity()})
    db_user = query.query(dto=dto)

    if db_user:
        _access_token = create_access_token(identity=db_user.user_id)

        return make_response(jsonify({
            'access_token': _access_token,
            # 'user_id': db_user.user_id,
            # 'refresh_token': get_fresh_token(identity=current_user)
        })), 200
    else:
        return make_response(jsonify({
            'message': 'User not found'
        })), 404


@identity_blueprint.route('/all', methods=['GET'])
@jwt_required()
def list_all_users(query: GetAllUsersQuery) -> Response:
    return make_response(jsonify(query.query()))


@identity_blueprint.route('/', methods=['GET', 'POST'])
@jwt_required()
@log_error()
def get_current_user(get_single_user_query: GetSingleUserQuery) -> Response:
    dto = get_dto(request, GetCurrentUserRequest, context={'current_user_id': get_jwt_identity()})
    response = get_single_user_query.query(dto)
    return make_response(jsonify(response)), 200  # type:ignore


@identity_blueprint.route('/get', methods=['GET', 'POST'])
@jwt_required()
@log_error()
def get_user(get_single_user_query: GetSingleUserQuery) -> Response:
    dto = get_dto(request, GetSingleUserRequest, context={'current_user_id': get_jwt_identity()})
    response = get_single_user_query.query(dto)
    return make_response(jsonify(response)), 200  # type:ignore


@identity_blueprint.route('/', methods=['DELETE'])
def delete_user():
    pass


@identity_blueprint.route('/change-passwd', methods=['POST'])
def request_change_password(request_to_change_password_uc: RequestToChangePasswordUC,
                            presenter: RequestingToChangePasswordResponseBoundary) -> Response:
    try:
        dto = get_dto(request, RequestingToChangePasswordRequest, context={})
        request_to_change_password_uc.execute(dto)

        return presenter.response, 200  # type:ignore
    except Exception as exc:
        if current_app.debug:
            logger.exception(exc)

        return make_response(jsonify({'messages': exc.args})), 400  # type:ignore


@identity_blueprint.route('/change-passwd/<string:reset_token>', methods=['POST'])
def change_password(reset_token: str, change_password_uc: ChangePasswordUC,
                    presenter: ChangingPasswordResponseBoundary) -> Response:
    try:
        dto = get_dto(request, ResettingPasswordRequest, context={'reset_token': reset_token})
        change_password_uc.execute_reset(dto)

        return presenter.response, 200  # type:ignore
    except Exception as exc:
        if current_app.debug:
            raise exc

        return make_response(jsonify({'messages': exc.args})), 400  # type:ignore


@identity_blueprint.route('/change-passwd/authorized', methods=['POST'])
@jwt_required()
def change_password_authorizedly(change_password_uc: ChangePasswordUC,
                                 presenter: ChangingPasswordResponseBoundary) -> Response:
    try:
        current_user = get_jwt_identity()
        dto = get_dto(request, ChangingPasswordRequest, context={'current_user': current_user})
        change_password_uc.execute_change(dto)

        return presenter.response, 200  # type:ignore
    except Exception as exc:
        if current_app.debug:
            logger.exception(exc)

        return make_response(jsonify({'messages': exc.args})), 400  # type:ignore


class RegisteringAccountPresenter(RegisteringAccountResponseBoundary):
    response: Response

    def present(self, response_dto: RegisteringUserResponse) -> None:
        _access_token = create_access_token(identity=response_dto.user_id)
        _refresh_token = create_refresh_token(identity=response_dto.email)

        # update response_dto with access_token and refresh_token
        response_dto = _merge_dict(
            response_dto.__dict__,
            {
                'access_token': _access_token,
                'refresh_token': _refresh_token
            }
        )
        self.response = make_response(jsonify(response_dto))


class LoggingUserInPresenter(LoggingUserInResponseBoundary):
    response: Response

    def present(self, response_dto: Union[LoggedUserResponse, FailedLoginResponse]) -> None:
        if isinstance(response_dto, LoggedUserResponse):
            self.response = make_response(jsonify(response_dto))
        else:
            self.response = make_response(jsonify(response_dto), 401, {})


class RequestingToChangePasswordPresenter(RequestingToChangePasswordResponseBoundary):
    response: Response

    def present(self, response_dto: RequestingToChangePasswordResponse) -> None:
        self.response = make_response(jsonify(response_dto))


class ChangingPasswordPresenter(ChangingPasswordResponseBoundary):
    response: Response

    def present(self, response_dto: ChangingPasswordResponse) -> None:
        # TODO: Read more here to find way for invalidating the JWT token before sending to client a new one. At this
        #  point I wrote this line, the new JWT token has been sent but User still can use the old JWT token to login
        _access_token = create_access_token(identity=response_dto.user_id)
        _refresh_token = create_refresh_token(identity=response_dto.email)

        # update response_dto with access_token and refresh_token
        response_dto = _merge_dict(
            response_dto.__dict__, {
                'access_token': _access_token,
                'refresh_token': _refresh_token
            }
        )

        self.response = make_response(jsonify(response_dto))


def _merge_dict(dict1, dict2):
    dict1.update(dict2)
    return dict1
