#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector
from auth.application.services.authentication_unit_of_work import AuthenticationUnitOfWork
from auth.application.usecases.log_user_in import LoggingUserInUC, LoggingUserInResponseBoundary
from auth.application.usecases.register_user import RegisteringUserUC, RegisteringUserResponseBoundary

__all__ = [
    # module
    'AuthenticationModule'
]


class AuthenticationModule(injector.Module):
    @injector.provider
    def register_user_uc(self, boundary: RegisteringUserResponseBoundary,
                         uow: AuthenticationUnitOfWork) -> RegisteringUserUC:
        return RegisteringUserUC(boundary, uow)

    @injector.provider
    def login_uc(self,
                 boundary: LoggingUserInResponseBoundary,
                 uow: AuthenticationUnitOfWork) -> LoggingUserInUC:
        return LoggingUserInUC(boundary, uow)
