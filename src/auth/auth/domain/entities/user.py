#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

from auth.domain.rules.email_must_be_valid_address_rule import EmailMustBeValidAddressRule
from auth.domain.rules.email_must_not_be_empty_rule import EmailMustNotBeEmptyRule
from auth.domain.rules.password_must_meet_requirement_rule import PasswordMustMeetRequirementRule
from foundation.entity import Entity
from foundation.events import EventMixin
from passlib.hash import pbkdf2_sha256 as sha256


class User(EventMixin, Entity):
    def __init__(
            self,
            email: str,
            password: str
    ):
        # check rules
        self.check_rule(EmailMustNotBeEmptyRule(email=email))
        self.check_rule(EmailMustBeValidAddressRule(email=email))
        self.check_rule(PasswordMustMeetRequirementRule(password=password))

        self.email = email
        self.password = User.generate_hash(password)
        self.active = True

        # set roles
        self._roles = set()

    @property
    def id(self):
        return self._id

    @staticmethod
    def create(
            email: str,
            password: str,
    ) -> User:
        return User(
            email=email,
            password=password
        )

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)

    def verify_password(self, password):
        return User.verify_hash(password, self.password)
