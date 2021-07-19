#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector

from foundation import AsyncHandler, AsyncEventHandlerProvider
from foundation.domain_events.shop_events import ShopRegistrationConfirmedEvent
from foundation.events import EveryModuleMustCatchThisEvent
from identity.application.services.identity_unit_of_work import IdentityUnitOfWork
from identity.domain.events.user_registration_confirmed_event import UserRegistrationConfirmedEvent
from identity.identity_handler_facade import IdentityHandlerFacade, Identity_CatchAllEventHandler, \
    UserRegistrationConfirmedEventHandler, CreateUserWhileShopRegistrationConfirmedEventHandler


class IdentityEventHandlerModule(injector.Module):
    @injector.provider
    def facade(self, uow: IdentityUnitOfWork) -> IdentityHandlerFacade:
        return IdentityHandlerFacade(uow)

    def configure(self, binder: injector.Binder) -> None:
        binder.multibind(AsyncHandler[EveryModuleMustCatchThisEvent],
                         to=AsyncEventHandlerProvider(Identity_CatchAllEventHandler))

        binder.multibind(AsyncHandler[UserRegistrationConfirmedEvent],
                         to=AsyncEventHandlerProvider(UserRegistrationConfirmedEventHandler))

        binder.multibind(AsyncHandler[ShopRegistrationConfirmedEvent],
                         to=AsyncEventHandlerProvider(CreateUserWhileShopRegistrationConfirmedEventHandler))