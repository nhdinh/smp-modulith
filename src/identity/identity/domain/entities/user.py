#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import datetime
from enum import Enum
import secrets
import uuid

from passlib.hash import pbkdf2_sha256 as sha256

from foundation.domain_events.identity_events import ShopAdminCreatedEvent, UserCreatedEvent
from foundation.entity import Entity
from foundation.events import EventMixin, EveryModuleMustCatchThisEvent, new_event_id

from identity.adapters.id_generator import generate_user_id
from identity.domain.events.password_resetted_event import PasswordResettedEvent
from identity.domain.events.request_password_change_created_event import RequestPasswordChangeCreatedEvent
from identity.domain.rules.email_must_be_valid_address_rule import EmailMustBeValidAddressRule
from identity.domain.rules.email_must_not_be_empty_rule import EmailMustNotBeEmptyRule
from identity.domain.rules.password_must_meet_requirement_rule import PasswordMustMeetRequirementRule
from identity.domain.value_objects import UserId


class UserStatus(Enum):
    NORMAL = 'NORMAL'
    DISABLED = 'DISABLED'
    DELETED = 'DELETED'


class User(EventMixin, Entity):
    email: str
    reset_password_token: str

    def __init__(
            self,
            user_id: UserId,
            email: str,
            hashed_password: str,
            **kwargs
    ):
        """

        :param user_id:
        :param email:
        :param hashed_password:
        :param emit_shop_creation_event: bool flag to indicate that the new shop will be created after this user creation.
        """
        super(User, self).__init__()

        # check rules
        self.check_rule(EmailMustNotBeEmptyRule(email=email))
        self.check_rule(EmailMustBeValidAddressRule(email=email))
        # self.check_rule(PasswordMustMeetRequirementRule(password=password))

        self.user_id = user_id
        self.email = email
        self.mobile = kwargs.get('mobile', '')

        self.password = hashed_password
        self.status = UserStatus.NORMAL

        # set roles
        self._roles = set()

        # set time data
        self.confirmed_at = datetime.now()
        self.current_login_at = datetime.now()
        self.current_login_ip = ''
        self.login_count = 0

        # change password token
        self.reset_password_token = ''
        self.request_reset_password_at = None

        self._record_event(UserCreatedEvent(
            event_id=new_event_id(),
            user_id=self.user_id,
            email=self.email,
            mobile=self.mobile,
            created_at=datetime.now(),
        ))

        if kwargs.get('emit_shop_creation_event'):
            self._record_event(ShopAdminCreatedEvent(
                event_id=new_event_id(),
                user_id=self.user_id,
                email=self.email,
                mobile=self.mobile,
                created_at=datetime.now(),
            ))

    @staticmethod
    def create(
            email: str,
            password: str,
            mobile: str = '',
            is_plain_password: bool = True,
            on_shop_confirmation: bool = False,
    ) -> User:
        """
        Create an instance of SystemUser

        :param email:
        :param password:
        :param mobile:
        :param is_plain_password:
        :param on_shop_confirmation: a flag that indicates whether the new shop will be created upon this user creation.

        :return:
        """
        if is_plain_password:
            password = User.generate_hash(password)

        return User(
            user_id=generate_user_id(),
            email=email,
            hashed_password=password,
            mobile=mobile,
            emit_shop_creation_event=on_shop_confirmation,
        )

    @staticmethod
    def generate_hash(plain_string: str) -> str:
        """
        Generate SHA256 hash from a string

        :param plain_string: a plain text string
        :return: its hash
        """
        return sha256.hash(plain_string)

    @staticmethod
    def verify_hash(plain_string: str, hashed_string: str) -> bool:
        """
        To verify a PLAIN string with a HASHED string to see if they are equal.

        :param plain_string: a text-based plain string
        :param hashed_string: a hashed string
        :return: matched or not
        """
        return sha256.verify(plain_string, hashed_string)

    def verify_password(self, password) -> bool:
        """
        Verify self hashed_password with the input plain one.

        :param password: the plain password to verify
        :return: matched or not
        """
        return User.verify_hash(password, self.password)

    def create_new_password_change_token(self) -> None:
        self.reset_password_token = secrets.token_urlsafe(64)
        self.request_reset_password_at = datetime.now()

        self._record_event(RequestPasswordChangeCreatedEvent(
            username=self.email,
            email=self.email,
            token=self.reset_password_token
        ))

    def change_password(self, new_password: str) -> None:
        """
        Change current password to a new one.

        This method will verify the password against password rule. If the new password is strong enough, this will
        hash the plain new password and persist it with self model.

        :param new_password: New password
        """
        self.check_rule(PasswordMustMeetRequirementRule(password=new_password))
        self.password = User.generate_hash(new_password)

        # remove token
        self.reset_password_token = ''
        self.request_reset_password_at = None

        self._record_event(PasswordResettedEvent(
            username=self.email,
            email=self.email
        ))

    def update_login_status(self, remote_address: str):
        self.current_login_ip = remote_address
        self.login_count += 1

        self._record_event(EveryModuleMustCatchThisEvent(event_id=uuid.uuid4()))
