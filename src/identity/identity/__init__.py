#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector
from sqlalchemy.engine import Connection

from facade import IdentityModuleFacade
from foundation.events import AsyncHandler, AsyncEventHandlerProvider
from identity.config import IdentityModuleConfig
from identity.domain.events.user_registration_confirmed_event import UserRegistrationConfirmedEvent


class IdentityModule(injector.Module):
    @injector.provider
    def facade(self, module_config: IdentityModuleConfig, connection: Connection) -> IdentityModuleFacade:
        return IdentityModuleFacade(module_config, connection)

    def configure(self, binder: injector.Binder) -> None:
        binder.multibind(AsyncHandler[UserRegistrationConfirmedEvent],
                         to=AsyncEventHandlerProvider(UserRegistrationConfirmedEventHandler))


class UserRegistrationConfirmedEventHandler:
    @injector.inject
    def __init__(self, facade: IdentityModuleFacade) -> None:
        self._facade = facade

    def __call__(self, event: UserRegistrationConfirmedEvent) -> None:
        self._facade.create_user()
