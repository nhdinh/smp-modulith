#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations
import uuid
import secrets
from passlib.hash import pbkdf2_sha256 as sha256
from foundation.entity import Entity
from foundation.events import EventMixin
from store import CountStoreOwnerByEmailQuery
from store.domain.entities.registration_status import RegistrationStatus, RegistrationWaitingForConfirmation
from store.domain.entities.value_objects import RegistrationId
from store.domain.rules.store_name_must_not_be_empty_rule import StoreNameMustNotBeEmptyRule
from store.domain.rules.user_email_must_be_unique_rule import UserEmailMustBeUniqueRule
from store.domain.rules.user_email_must_be_valid_rule import UserEmailMustBeValidRule
from store.domain.rules.user_mobile_must_be_valid_rule import UserMobileMustBeValidRule


class StoreRegistration(EventMixin, Entity):
    def __init__(
            self,
            registration_id: RegistrationId,
            store_name: str,
            owner_email: str,
            owner_mobile: str,
            owner_password: str,
            confirmation_token: str,
            status: RegistrationStatus = RegistrationWaitingForConfirmation,
    ):
        super(StoreRegistration, self).__init__()

        self.check_rule(StoreNameMustNotBeEmptyRule(store_name))
        self.check_rule(UserEmailMustBeValidRule(owner_email))
        self.check_rule(UserMobileMustBeValidRule(owner_mobile))
        self.check_rule(UserEmailMustBeUniqueRule(owner_email))

        self.registration_id = registration_id
        self.store_name = store_name
        self.owner_email = owner_email
        self.owner_mobile = owner_mobile
        self.owner_password = owner_password
        self.confirmation_token = confirmation_token
        self.status = status

    @staticmethod
    def create_registration(
            store_name: str,
            owner_email: str,
            owner_password: str,
            owner_mobile: str,
    ):
        new_guid = uuid.uuid4()

        registration = StoreRegistration(
            registration_id=new_guid,
            store_name=store_name,
            owner_email=owner_email,
            owner_password=sha256.hash(owner_password),
            owner_mobile=owner_mobile,
            confirmation_token=StoreRegistration._create_confirmation_token(),
            status=RegistrationWaitingForConfirmation
        )

    def confirm_registration(self, registration: StoreRegistration):
        """
        Confirm a registration and create new store and user together

        :param registration:
        :return:
        """
        if registration.status == RegistrationWaitingForConfirmation:
            registration.create_store_owner()
            registration.create_store()
        else:
            pass

    @staticmethod
    def _create_confirmation_token():
        return secrets.token_urlsafe(64)

    def create_store_owner(self):
        pass

    def create_store(self):
        pass
