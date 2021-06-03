#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations
import uuid
from uuid import UUID
import secrets
from passlib.hash import pbkdf2_sha256 as sha256
from foundation.entity import Entity
from foundation.events import EventMixin
from store.domain.entities.value_objects import RegistrationId

NEW_REGISTRATION = 'new_registration'
REGISTRATION_ACTIVATED = 'registration_activated'


class StoreRegistration(EventMixin, Entity):
    def __init__(
            self,
            registration_id: RegistrationId,
            store_name: str,
            owner_email: str,
            owner_mobile: str,
            owner_password: str,
            confirmation_token: str,
            status=NEW_REGISTRATION
    ):
        super(StoreRegistration, self).__init__()

        self.check_rule(StoreNameMustNotBeEmptyRule(store_name))
        self.check_rule(UserEmailMustNotBeEmptyRule(owner_email))
        self.check_rule(UserMobileMustNotBeEmptyRule(owner_mobile))

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
            status=NEW_REGISTRATION
        )

    def confirm_registration(self, registration: StoreRegistration):
        """
        Confirm a registration and create new store and user together

        :param registration:
        :return:
        """
        if registration.status == NEW_REGISTRATION:
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
