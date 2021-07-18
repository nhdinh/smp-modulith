#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Union

import injector

from foundation.domain_events.shop_events import ShopRegistrationConfirmedEvent
from foundation.events import AsyncHandler, AsyncEventHandlerProvider, EveryModuleMustCatchThisEvent
from foundation.logger import logger
from identity.application.services.authentication_unit_of_work import AuthenticationUnitOfWork
from identity.domain.events.user_registration_confirmed_event import UserRegistrationConfirmedEvent
from identity.identity_handler_facade import IdentityHandlerFacade, IdentityHandlerFacade


class IdentityEventHandlerModule(injector.Module):
    @injector.provider
    def facade(self, uow: AuthenticationUnitOfWork) -> IdentityHandlerFacade:
        return IdentityHandlerFacade(uow)

    def configure(self, binder: injector.Binder) -> None:
        binder.multibind(AsyncHandler[EveryModuleMustCatchThisEvent],
                         to=AsyncEventHandlerProvider(Identity_CatchAllEventHandler))

        binder.multibind(AsyncHandler[UserRegistrationConfirmedEvent],
                         to=AsyncEventHandlerProvider(UserRegistrationConfirmedEventHandler))

        binder.multibind(AsyncHandler[ShopRegistrationConfirmedEvent],
                         to=AsyncEventHandlerProvider(CreateUserWhileShopRegistrationConfirmedEventHandler))


class UserRegistrationConfirmedEventHandler:
    @injector.inject
    def __init__(self, facade: IdentityHandlerFacade) -> None:
        self._facade = facade

    def __call__(self, event: Union[UserRegistrationConfirmedEvent]) -> None:
        email = event.email
        mobile = event.mobile
        hashed_password = event.hashed_password

        self._facade.create_user(
            email=email,
            mobile=mobile,
            hashed_password=hashed_password,
        )


class CreateUserWhileShopRegistrationConfirmedEventHandler:
    @injector.inject
    def __init__(self, facade: IdentityHandlerFacade) -> None:
        self._facade = facade

    def __call__(self, event: Union[ShopRegistrationConfirmedEvent]) -> None:
        try:
            event_id = event.event_id
            registration_id = event.registration_id
            user_email = event.user_email
            user_hashed_password = event.user_hashed_password
            mobile = event.mobile

            self._facade.create_user(
                email=user_email,
                mobile=mobile,
                hashed_password=user_hashed_password
            )
        except Exception as exc:
            # do something
            logger.exception(exc)
            raise exc


class Identity_CatchAllEventHandler:
    @injector.inject
    def __init__(self):
        ...

    def __call__(self, event: EveryModuleMustCatchThisEvent):
        logger.debug(f'Identity_{event.event_id}')
