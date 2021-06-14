#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Union

import injector
from sqlalchemy.engine import Connection

from foundation.events import AsyncHandler, AsyncEventHandlerProvider
from identity.config import IdentityModuleConfig
from identity.domain.events.user_registration_confirmed_event import UserRegistrationConfirmedEvent
from identity_handler_facade import IdentityHandlerFacade


class IdentityModule(injector.Module):
    @injector.provider
    def facade(self, connection: Connection) -> IdentityHandlerFacade:
        return IdentityHandlerFacade(connection)

    def configure(self, binder: injector.Binder) -> None:
        binder.multibind(AsyncHandler[UserRegistrationConfirmedEvent],
                         to=AsyncEventHandlerProvider(UserRegistrationConfirmedEventHandler))


class UserRegistrationConfirmedEventHandler:
    @injector.inject
    def __init__(self, facade: IdentityHandlerFacade) -> None:
        self._facade = facade

    def __call__(self, event: Union[UserRegistrationConfirmedEvent]) -> None:
        user_id = event.user_id
        email = event.email
        mobile = event.mobile
        hashed_password = event.hashed_password

        self._facade.create_user(
            user_id=user_id,
            email=email,
            mobile=mobile,
            hashed_password=hashed_password,
        )
