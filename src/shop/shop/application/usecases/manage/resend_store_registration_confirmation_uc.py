#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from datetime import datetime, timedelta

from foundation.events import ThingGoneInBlackHoleError
from shop.application.services.shop_unit_of_work import ShopUnitOfWork
from shop.domain.entities.value_objects import RegistrationStatus, ExceptionMessages

ALLOWABLE_RESEND_DURATION = timedelta(minutes=0)


@dataclass
class ResendingRegistrationConfirmationResponse:
    status: bool


class ResendingRegistrationConfirmationResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: ResendingRegistrationConfirmationResponse):
        raise NotImplementedError


@dataclass
class ResendingRegistrationConfirmationRequest:
    registration_email: str


class ResendRegistrationConfirmationUC:
    def __init__(self, ob: ResendingRegistrationConfirmationResponseBoundary, uow: ShopUnitOfWork):
        self._ob = ob
        self._uow = uow

    def execute(self, dto: ResendingRegistrationConfirmationRequest):
        with self._uow as uow:  # type:ShopUnitOfWork
            try:
                registration = uow.shops.get_registration_by_email(
                    email=dto.registration_email)  # type:ShopRegistration

                if not registration:
                    raise ThingGoneInBlackHoleError(ExceptionMessages.REGISTRATION_NOT_FOUND)

                if registration.status != RegistrationStatus.REGISTRATION_WAITING_FOR_CONFIRMATION:
                    raise Exception(ExceptionMessages.REGISTRATION_HAS_BEEN_CONFIRMED)

                if registration.last_resend is not None and datetime.now() - registration.last_resend < ALLOWABLE_RESEND_DURATION:
                    raise Exception(ExceptionMessages.REGISTRATION_RESEND_TOO_MUCH)

                if registration.status == RegistrationStatus.REGISTRATION_WAITING_FOR_CONFIRMATION and registration.expired:
                    raise Exception(ExceptionMessages.REGISTRATION_HAS_BEEN_EXPIRED)

                registration.resend_confirmation_link()

                response = ResendingRegistrationConfirmationResponse(status=True)
                self._ob.present(response_dto=response)

                uow.commit()
            except Exception as exc:
                raise exc
