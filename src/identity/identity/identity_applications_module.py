#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector
from sqlalchemy.engine import Connection

from identity.application.queries.identity_queries import (
    CountRevokedTokenByJTIQuery,
    GetSingleUserQuery,
    SqlCountRevokedTokenByJTIQuery,
    SqlGetSingleUserQuery,
)
from identity.application.services.identity_unit_of_work import IdentityUnitOfWork
from identity.application.usecases.change_password_uc import ChangePasswordUC, ChangingPasswordResponseBoundary
from identity.application.usecases.log_user_in_uc import LoggingUserInResponseBoundary, LoggingUserInUC
from identity.application.usecases.register_user_uc import RegisteringUserResponseBoundary, RegisteringUserUC
from identity.application.usecases.request_to_change_password_uc import (
    RequestingToChangePasswordResponseBoundary,
    RequestToChangePasswordUC,
)
from identity.application.usecases.revoke_token_uc import RevokingTokenUC


class IdentityApplicationModule(injector.Module):
    @injector.provider
    def register_user_uc(self, boundary: RegisteringUserResponseBoundary,
                         uow: IdentityUnitOfWork) -> RegisteringUserUC:
        return RegisteringUserUC(output_boundary=boundary, uow=uow)

    @injector.provider
    def login_uc(self,
                 boundary: LoggingUserInResponseBoundary,
                 uow: IdentityUnitOfWork) -> LoggingUserInUC:
        return LoggingUserInUC(output_boundary=boundary, uow=uow)

    @injector.provider
    def revoke_token_uc(self, uow: IdentityUnitOfWork) -> RevokingTokenUC:
        return RevokingTokenUC(uow=uow)

    @injector.provider
    def request_change_password_uc(
            self,
            ob: RequestingToChangePasswordResponseBoundary,
            uow: IdentityUnitOfWork
    ) -> RequestToChangePasswordUC:
        return RequestToChangePasswordUC(ob, uow)

    @injector.provider
    def change_password_uc(self, ob: ChangingPasswordResponseBoundary,
                           uow: IdentityUnitOfWork) -> ChangePasswordUC:
        return ChangePasswordUC(ob, uow)

    @injector.provider
    def get_single_user_query(self, conn: Connection) -> GetSingleUserQuery:
        return SqlGetSingleUserQuery(connection=conn)

    @injector.provider
    def get_revoked_token_query(self, conn: Connection) -> CountRevokedTokenByJTIQuery:
        return SqlCountRevokedTokenByJTIQuery(connection=conn)
