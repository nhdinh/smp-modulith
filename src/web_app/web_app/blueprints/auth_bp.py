#!/usr/bin/env python
# -*- coding: utf-8 -*-
import flask_injector
import injector
from flask import Blueprint, Response, make_response, jsonify, request, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt

from foundation.business_rule import BusinessRuleValidationError
from identity.application.queries.identity import GetAllUsersQuery, GetSingleUserQuery
from identity.application.usecases.change_password_uc import ChangingPasswordResponseBoundary, ChangePasswordUC, \
    ResettingPasswordRequest, ChangingPasswordResponse, ChangingPasswordRequest
from identity.application.usecases.log_user_in import LoggingUserInUC, LoggingUserInResponseBoundary, \
    LoggedUserResponse, \
    LoggingUserInRequest
from identity.application.usecases.register_user import RegisteringUserUC, RegisteringUserResponseBoundary, \
    RegisteringUserRequest, RegisteringUserResponse
from identity.application.usecases.request_to_change_password_uc import RequestingToChangePasswordResponseBoundary, \
    RequestingToChangePasswordResponse, RequestToChangePasswordUC, RequestingToChangePasswordRequest
from identity.application.usecases.revoke_token import RevokingTokenUC
from identity.domain.entities.revoked_token import RevokedToken
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

    @injector.provider
    @flask_injector.request
    def request_to_change_password_response_boundary(self) -> RequestingToChangePasswordResponseBoundary:
        return RequestingToChangePasswordPresenter()

    @injector.provider
    @flask_injector.request
    def change_password_response_boundary(self) -> ChangingPasswordResponseBoundary:
        return ChangingPasswordPresenter()


@auth_blueprint.route('/register', methods=['POST'], strict_slashes=False)
def register_user(registering_user_uc: RegisteringUserUC, presenter: RegisteringUserResponseBoundary):
    """
    Register a new user account

    :param registering_user_uc: The usecase processor named RegisteringUser
    :param presenter: the output present formatter
    :return:
    """
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
    # UserLogin
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
def user_logout_access(revoking_token_uc: RevokingTokenUC):
    jti = get_jwt()['jti']
    try:
        revoked_token = RevokedToken(jti=jti)
        revoking_token_uc.execute(revoked_token)

        return make_response(jsonify({'message': 'Access token has been revoked'}))
    except Exception as exc:
        if current_app.debug:
            raise exc

        return make_response(jsonify({'message': 'Something wrong'})), 500


@auth_blueprint.route('/logout/refresh', methods=['POST'])
@jwt_required(refresh=True)
def user_logout_refresh(revoking_token_uc: RevokingTokenUC):
    jti = get_jwt()['jti']
    try:
        revoked_token = RevokedToken(jti=jti)
        revoking_token_uc.execute(revoked_token)

        return make_response(jsonify({'message': 'Refresh token has been revoked'}))
    except Exception as exc:
        if current_app.debug:
            raise exc

        return make_response(jsonify({'message': 'Something wrong'})), 500


@auth_blueprint.route('/refresh-token', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token(query: GetSingleUserQuery):
    # TokenRefresh
    current_user = get_jwt_identity()
    db_user = query.query(user_q=current_user)

    if db_user:
        _access_token = create_access_token(identity=current_user)

        return make_response(jsonify({
            'access_token': _access_token,
            'username': current_user,
            # 'refresh_token': get_fresh_token(identity=current_user)
        })), 200
    else:
        return make_response(jsonify({
            'message': 'User not found'
        })), 404


@auth_blueprint.route('/all', methods=['GET'])
@jwt_required()
def list_all_users(query: GetAllUsersQuery) -> Response:
    return make_response(jsonify(query.query()))


@auth_blueprint.route('/', methods=['GET'])
@jwt_required()
def get_current_user(query: GetSingleUserQuery) -> Response:
    current_user = get_jwt_identity()
    return make_response(jsonify(query.query(user_q=current_user)))


@auth_blueprint.route('/', methods=['DELETE'])
def delete_user():
    pass


@auth_blueprint.route('/change-passwd', methods=['POST'])
def request_change_password(request_to_change_password_uc: RequestToChangePasswordUC,
                            presenter: RequestingToChangePasswordResponseBoundary) -> Response:
    try:
        dto = get_dto(request, RequestingToChangePasswordRequest, context={})
        request_to_change_password_uc.execute(dto)

        return presenter.response, 200  # type:ignore
    except Exception as exc:
        if current_app.debug:
            raise exc

        return make_response(jsonify({'messages': exc.args})), 400  # type:ignore


@auth_blueprint.route('/change-passwd/<string:reset_token>', methods=['POST'])
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


@auth_blueprint.route('/change-passwd/authorized', methods=['POST'])
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
            raise exc

        return make_response(jsonify({'messages': exc.args})), 400  # type:ignore


class RegisteringUserPresenter(RegisteringUserResponseBoundary):
    response: Response

    def present(self, response_dto: RegisteringUserResponse) -> None:
        _access_token = create_access_token(identity=response_dto.email)
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

    def present(self, response_dto: LoggedUserResponse) -> None:
        _access_token = create_access_token(identity=response_dto.username)
        _refresh_token = create_refresh_token(identity=response_dto.username)

        # update response_dto with access_token and refresh_token
        response_dto = _merge_dict(
            response_dto.__dict__,
            {
                'access_token': _access_token,
                'refresh_token': _refresh_token
            }
        )
        self.response = make_response(jsonify(response_dto))


class RequestingToChangePasswordPresenter(RequestingToChangePasswordResponseBoundary):
    response: Response

    def present(self, response_dto: RequestingToChangePasswordResponse) -> None:
        self.response = make_response(jsonify(response_dto))


class ChangingPasswordPresenter(ChangingPasswordResponseBoundary):
    response: Response

    def present(self, response_dto: ChangingPasswordResponse) -> None:
        # TODO: Read more here to find way for invalidating the JWT token before sending to client a new one. At this
        #  point I wrote this line, the new JWT token has been sent but User still can use the old JWT token to login
        _access_token = create_access_token(identity=response_dto.email)
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


def _merge_dict(dict1, dict2):
    dict1.update(dict2)
    return dict1
