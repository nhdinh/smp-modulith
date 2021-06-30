#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import secrets
import uuid
from datetime import datetime, timedelta

from foundation.entity import Entity
from foundation.events import EventMixin
from store.application.services.user_counter_services import UserCounters
from store.domain.entities import store_warehouse
from store.domain.entities.registration_status import RegistrationStatus, RegistrationWaitingForConfirmation, \
    RegistrationConfirmed
from store.domain.entities.store import Store
from store.domain.entities.store_owner import StoreOwner
from store.domain.entities.store_warehouse import StoreWarehouse
from store.domain.entities.value_objects import RegistrationId, StoreId
from store.domain.events.store_registered_event import StoreRegisteredEvent, StoreRegistrationResendEvent
from store.domain.rules.store_name_must_not_be_empty_rule import StoreNameMustNotBeEmptyRule
from store.domain.rules.store_registration_must_have_valid_expiration_rule import \
    StoreRegistrationMustHaveValidExpirationRule
from store.domain.rules.store_registration_must_have_valid_token_rule import StoreRegistrationMustHaveValidTokenRule
from store.domain.rules.user_email_must_be_unique_rule import UserEmailMustBeUniqueRule
from store.domain.rules.user_email_must_be_valid_rule import UserEmailMustBeValidRule
from store.domain.rules.user_mobile_must_be_valid_rule import UserMobileMustBeValidRule


class StoreRegistration(EventMixin, Entity):
    confirmation_token: str

    def __init__(
            self,
            registration_id: RegistrationId,
            store_name: str,
            owner_email: str,
            owner_mobile: str,
            owner_password: str,
            confirmation_token: str,
            status: RegistrationStatus,
            last_resend: datetime,
            user_counter_services: UserCounters,
            version: int = 0,
    ):
        super(StoreRegistration, self).__init__()
        self.check_rule(StoreNameMustNotBeEmptyRule(store_name))
        self.check_rule(UserEmailMustBeValidRule(owner_email))
        self.check_rule(UserMobileMustBeValidRule(owner_mobile))
        self.check_rule(UserEmailMustBeUniqueRule(owner_email, user_counter_services))

        self.registration_id = registration_id
        self._store_registration_id = registration_id
        self._owner_id = registration_id

        self.store_name = store_name

        self.owner_email = owner_email
        self.owner_mobile = owner_mobile
        self.owner_password = owner_password

        self.confirmation_token = confirmation_token
        self.status = status
        self.confirmed_at = None
        self.last_resend = last_resend
        self.version = version

        # add domain event
        self._record_event(StoreRegisteredEvent(
            self.registration_id,
            self.store_name,
            self.owner_email,
            self.confirmation_token
        ))

    @property
    def store_name(self):
        return self._name

    @store_name.setter
    def store_name(self, value):
        self._name = value

    @property
    def expired(self):
        return (datetime.now() - self.created_at) > timedelta(days=2)

    @staticmethod
    def create_registration(
            store_name: str,
            owner_email: str,
            owner_password: str,
            owner_mobile: str,
            user_counter_services: UserCounters
    ):
        new_guid = uuid.uuid4()

        registration = StoreRegistration(
            registration_id=new_guid,
            store_name=store_name,
            owner_email=owner_email,
            owner_password=owner_password,
            owner_mobile=owner_mobile,
            confirmation_token=StoreRegistration._create_confirmation_token(),
            status=RegistrationWaitingForConfirmation,
            version=1,
            last_resend=datetime.now(),
            user_counter_services=user_counter_services,
        )

        return registration

    def confirm(self):
        """
        Confirm a registration and create new store and user together

        :return:
        """
        self.check_rule(StoreRegistrationMustHaveValidTokenRule(registration=self))
        self.check_rule(StoreRegistrationMustHaveValidExpirationRule(registration=self))

        self.status = RegistrationConfirmed
        self.confirmed_at = datetime.today()

        # self._record_event(StoreRegistrationConfirmedEvent(
        #     store_id=self.registration_id,
        #     store_name=self.store_name,
        #     owner_id=self.registration_id,
        #     email=self.owner_email,
        #     mobile=self.owner_mobile,
        #     hashed_password=self.owner_password,
        # ))

        return self.registration_id

    def create_store_owner(self) -> StoreOwner:
        # check rule
        return StoreOwner(
            id=self.registration_id,
            email=self.owner_email,
            mobile=self.owner_mobile,
            hashed_password=self.owner_password,
            confirmed_at=datetime.now(),
        )

    def create_store(self, owner: StoreOwner) -> Store:
        # check rule
        return Store.create_store_from_registration(
            store_id=self.registration_id,
            store_name=self.store_name,
            store_owner=owner
        )

    def create_default_warehouse(self, store_id: StoreId, owner: StoreOwner) -> StoreWarehouse:
        return StoreWarehouse(
            warehouse_id=self.registration_id,
            store_id=store_id,
            warehouse_owner=owner.email,
            warehouse_name=self.store_name,
            default=True
        )

    @staticmethod
    def _create_confirmation_token():
        return secrets.token_urlsafe(64)

    def resend_confirmation_link(self):
        # make new confirmation token
        self.confirmation_token = StoreRegistration._create_confirmation_token()
        self.last_resend = datetime.now()
        self.version += 1

        # add domain event
        self._record_event(StoreRegistrationResendEvent(
            self.registration_id,
            self.store_name,
            self.owner_email,
            self.confirmation_token
        ))
