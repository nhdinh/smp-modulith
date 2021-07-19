#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Union

import injector

from foundation.domain_events.shop_events import ShopRegistrationConfirmedEvent
from foundation.events import EveryModuleMustCatchThisEvent
from foundation.logger import logger
from identity import UserRegistrationConfirmedEvent
from identity.application.services.identity_unit_of_work import IdentityUnitOfWork
from identity.domain.entities import User


class IdentityHandlerFacade:
    def __init__(self, uow: IdentityUnitOfWork):
        self._uow = uow

    def create_user(self, email: str, mobile: str, hashed_password: str):
        with self._uow as uow:  # type: IdentityUnitOfWork
            try:
                user = User.create(email=email, password=hashed_password, is_plain_password=False, mobile=mobile)
                self._uow.identities.save(user)

                uow.commit()
            except Exception as exc:
                raise exc


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
    def __init__(self, facade: IdentityHandlerFacade):
        self._f = facade

    def __call__(self, event: EveryModuleMustCatchThisEvent):
        with self._f._uow as uow:  # type: IdentityUnitOfWork
            try:
                uow.commit()
            except Exception as exc:
                logger.exception(exc)
                raise exc
