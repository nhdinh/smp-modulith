#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import uuid
from datetime import datetime

from passlib.hash import pbkdf2_sha256 as sha256

from foundation.entity import Entity
from foundation.events import EventMixin
from identity.domain.rules.email_must_be_valid_address_rule import EmailMustBeValidAddressRule
from identity.domain.rules.email_must_not_be_empty_rule import EmailMustNotBeEmptyRule
from identity.domain.rules.password_must_meet_requirement_rule import PasswordMustMeetRequirementRule
from identity.domain.value_objects import UserId


class User(EventMixin, Entity):
    def __init__(
            self,
            user_id: UserId,
            email: str,
            password: str,
            **kwargs
    ):
        # check rules
        self.check_rule(EmailMustNotBeEmptyRule(email=email))
        self.check_rule(EmailMustBeValidAddressRule(email=email))
        self.check_rule(PasswordMustMeetRequirementRule(password=password))

        self._id = user_id
        self.email = email
        self.password = User.generate_hash(password=password)
        self.active = True

        # set roles
        self._roles = set()

    @property
    def id(self) -> UserId:
        return self._id

    @staticmethod
    def create(
            email: str,
            plain_password: str,
    ) -> User:
        return User(
            user_id=uuid.uuid4(),
            email=email,
            password=plain_password,
            registered_on=datetime.now(),
            admin=False
        )

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hashed_password):
        return sha256.verify(password, hashed_password)

    def verify_password(self, password):
        return User.verify_hash(password, self.password)
