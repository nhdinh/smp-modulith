#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector
from sqlalchemy.engine import Connection
from sqlalchemy.orm import sessionmaker

from identity.adapters import identity_db
from identity.application.services.authentication_unit_of_work import AuthenticationUnitOfWork

__all__ = [
    # module
    'AuthenticationInfrastructureModule'
]


class AuthenticationInfrastructureModule(injector.Module):
    @injector.provider
    def identity_db(self) -> identity_db:
        return identity_db

    @injector.provider
    def get_uow(self, conn: Connection) -> AuthenticationUnitOfWork:
        sessfactory = sessionmaker(bind=conn)
        return AuthenticationUnitOfWork(sessionfactory=sessfactory)
