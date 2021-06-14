#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector
from sqlalchemy.engine import Connection

from identity.application.queries.identity import SqlCountRevokedTokenByJTIQuery, SqlGetSingleUserQuery, \
    GetSingleUserQuery, CountRevokedTokenByJTIQuery
from identity.application.services.authentication_unit_of_work import AuthenticationUnitOfWork
from identity.application.usecases.change_password_uc import ChangePasswordUC, ChangingPasswordResponseBoundary
from identity.application.usecases.log_user_in import LoggingUserInUC, LoggingUserInResponseBoundary
from identity.application.usecases.register_user import RegisteringUserUC, RegisteringUserResponseBoundary
from identity.application.usecases.request_to_change_password_uc import RequestToChangePasswordUC, \
    RequestingToChangePasswordResponseBoundary
from identity.application.usecases.revoke_token import RevokingTokenUC

__all__ = [
    # module
    'AuthenticationModule'
]


class AuthenticationModule(injector.Module):
    @injector.provider
    def register_user_uc(self, boundary: RegisteringUserResponseBoundary,
                         uow: AuthenticationUnitOfWork) -> RegisteringUserUC:
        return RegisteringUserUC(output_boundary=boundary, uow=uow)

    @injector.provider
    def login_uc(self,
                 boundary: LoggingUserInResponseBoundary,
                 uow: AuthenticationUnitOfWork) -> LoggingUserInUC:
        return LoggingUserInUC(output_boundary=boundary, uow=uow)

    @injector.provider
    def revoke_token_uc(self, uow: AuthenticationUnitOfWork) -> RevokingTokenUC:
        return RevokingTokenUC(uow=uow)

    @injector.provider
    def request_change_password_uc(
            self,
            ob: RequestingToChangePasswordResponseBoundary,
            uow: AuthenticationUnitOfWork
    ) -> RequestToChangePasswordUC:
        return RequestToChangePasswordUC(ob, uow)

    @injector.provider
    def change_password_uc(self, ob: ChangingPasswordResponseBoundary,
                           uow: AuthenticationUnitOfWork) -> ChangePasswordUC:
        return ChangePasswordUC(ob, uow)

    @injector.provider
    def get_single_user_query(self, conn: Connection) -> GetSingleUserQuery:
        return SqlGetSingleUserQuery(connection=conn)

    @injector.provider
    def get_revoked_token_query(self, conn: Connection) -> CountRevokedTokenByJTIQuery:
        return SqlCountRevokedTokenByJTIQuery(connection=conn)
