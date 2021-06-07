#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector
from sqlalchemy.engine import Connection
from sqlalchemy.orm import sessionmaker

from foundation.events import EventBus
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
    def get_uow(self, conn: Connection, event_bus: EventBus) -> AuthenticationUnitOfWork:
        sessfactory = sessionmaker(bind=conn)
        return AuthenticationUnitOfWork(sessionfactory=sessfactory, event_bus=event_bus)
