#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations
import uuid
from uuid import UUID
import secrets

from foundation.entity import Entity
from foundation.events import EventMixin
from identity.domain.entities import User

NEW_REGISTRATION = 'new_registration'
REGISTRATION_ACTIVATED = 'registration_activated'


class StoreRegistration(EventMixin, Entity):
    def __init__(
            self,
            store_registration_id: UUID,
            store_name: str,
            owner: UUID,
            owner_email: str,
            owner_mobile: str,
            owner_password: str,
            confirmation_token: str,
            status=NEW_REGISTRATION
    ):
        super(StoreRegistration, self).__init__()

        self.store_registration_id = store_registration_id
        self.store_name = store_name
        self.owner = owner
        self.owner_email = owner_email
        self.owner_mobile = owner_mobile
        self.owner_password = owner_password
        self.confirmation_token = confirmation_token
        self.status = status

    @staticmethod
    def create_registration(
            store_name: str,
            owner: User
    ):
        if type(owner) == User:
            _owner_id = owner.id
        else:
            _owner_id = owner

        registration = StoreRegistration(
            store_registration_id=uuid.uuid4(),
            store_name=store_name,
            owner=_owner_id,
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
