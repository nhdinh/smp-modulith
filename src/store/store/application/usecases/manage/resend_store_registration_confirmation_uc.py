#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from datetime import datetime, timedelta

from store.application.services.store_unit_of_work import StoreUnitOfWork
from store.application.usecases.const import ExceptionMessages, ExceptionOfFindingThingInBlackHole
from store.domain.entities.store_registration import StoreRegistration
from store.domain.entities.registration_status import RegistrationStatus

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
    def __init__(self, ob: ResendingRegistrationConfirmationResponseBoundary, uow: StoreUnitOfWork):
        self._ob = ob
        self._uow = uow

    def execute(self, dto: ResendingRegistrationConfirmationRequest):
        with self._uow as uow:  # type:StoreUnitOfWork
            try:
                registration = uow.stores.fetch_registration_by_registration_email(
                    email=dto.registration_email)  # type:StoreRegistration

                if not registration:
                    raise ExceptionOfFindingThingInBlackHole(ExceptionMessages.REGISTRATION_NOT_FOUND)

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
