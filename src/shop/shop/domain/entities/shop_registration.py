#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import secrets
from datetime import datetime, timedelta

from foundation import Entity
from foundation import EventMixin, new_event_id
from shop.adapter.id_generators import SHOP_ID_PREFIX, generate_shop_id
from shop.domain.entities.shop import Shop
from shop.domain.entities.shop_user import ShopUser
from shop.domain.entities.shop_warehouse import ShopWarehouse
from shop.domain.entities.value_objects import (
    RegistrationStatus,
    ShopId,
    ShopRegistrationId,
    ShopUserType,
    SystemUserId,
)
from shop.domain.events import ShopRegistrationCreatedEvent, ShopRegistrationConfirmedEvent, ShopRegistrationResendEvent
from shop.domain.rules.shop_name_must_not_be_empty_rule import ShopNameMustNotBeEmptyRule
from shop.domain.rules.user_email_must_be_valid_rule import UserEmailMustBeValidRule
from shop.domain.rules.user_mobile_must_be_valid_rule import UserMobileMustBeValidRule


class ShopRegistration(EventMixin, Entity):
    confirmation_token: str

    def __init__(
            self,
            registration_id: ShopRegistrationId,
            shop_name: str,
            owner_email: str,
            owner_mobile: str,
            owner_password: str,
            confirmation_token: str,
            status: RegistrationStatus,
            last_resend: datetime,
            # user_counter_services: UserCounters,
            version: int = 0,
    ):
        super(ShopRegistration, self).__init__()
        self.check_rule(ShopNameMustNotBeEmptyRule(shop_name))
        self.check_rule(UserEmailMustBeValidRule(owner_email))
        self.check_rule(UserMobileMustBeValidRule(owner_mobile))
        # self.check_rule(UserEmailMustBeUniqueRule(owner_email, user_counter_services))

        # TODO: need refactoring
        self.registration_id = registration_id
        self._shop_registration_id = registration_id
        self._owner_id = registration_id

        self.shop_name = shop_name

        self.owner_email = owner_email
        self.owner_mobile = owner_mobile
        self.owner_password = owner_password

        self.confirmation_token = confirmation_token
        self.status = status
        self.confirmed_at = None
        self.last_resend = last_resend
        self.version = version

        # add domain event
        self._record_event(ShopRegistrationCreatedEvent, **dict(
            event_id=new_event_id(),
            registration_id=self.registration_id,
            shop_name=self.shop_name,
            owner_email=self.owner_email,
            password=self.owner_password,
            owner_mobile=self.owner_mobile,
            confirmation_token=self.confirmation_token
        ))

    @property
    def shop_name(self):
        return self._name

    @shop_name.setter
    def shop_name(self, value):
        self._name = value

    @property
    def expired(self):
        return (datetime.now() - self.created_at) > timedelta(days=2)

    @staticmethod
    def create_registration(
            shop_name: str,
            owner_email: str,
            owner_password: str,
            owner_mobile: str,
            # user_counter_services: UserCounters
    ):
        registration = ShopRegistration(
            registration_id=generate_shop_id(),
            shop_name=shop_name,
            owner_email=owner_email,
            owner_password=owner_password,
            owner_mobile=owner_mobile,
            confirmation_token=ShopRegistration._create_confirmation_token(),
            status=RegistrationStatus.REGISTRATION_WAITING_FOR_CONFIRMATION,
            version=1,
            last_resend=datetime.now(),
            # user_counter_services=user_counter_services,
        )

        return registration

    def confirm(self):
        """
        Confirm a registration and create new store and user together

        :return:
        """
        # TODO: Remove this
        # self.check_rule(StoreRegistrationMustHaveValidTokenRule(registration=self))
        # self.check_rule(StoreRegistrationMustHaveValidExpirationRule(registration=self))

        self.status = RegistrationStatus.REGISTRATION_CONFIRMED_YET_COMPLETED
        self.confirmed_at = datetime.now()

        # emit the event
        self._record_event(ShopRegistrationConfirmedEvent, **dict(
            event_id=new_event_id(),
            registration_id=self.registration_id,
            user_email=self.owner_email,
            user_hashed_password=self.owner_password,
            mobile=self.owner_mobile
        ))

        return self.registration_id

    def generate_shop_admin(self, user_id: SystemUserId, email: str, mobile: str) -> ShopUser:
        return ShopUser(
            user_id=user_id,
            email=email,
            mobile=mobile,
            shop_role=ShopUserType.ADMIN
        )

    def create_shop(self, shop_admin: ShopUser) -> 'Shop':
        if not self.registration_id.startswith(SHOP_ID_PREFIX):
            store_id = generate_shop_id()
        else:
            store_id = self.registration_id

        # check rule
        return Shop.create_shop_from_registration(
            shop_id=store_id,
            shop_name=self.shop_name,
            first_user=shop_admin
        )

    def create_default_warehouse(self, store_id: ShopId, owner: ShopUser) -> ShopWarehouse:
        raise NotImplementedError
        # if not self.registration_id.startswith('Warehouse'):
        #     store_id = generate_warehouse_id()
        # else:
        #     store_id = self.registration_id
        #
        # return ShopWarehouse(
        #     warehouse_id=store_id,
        #     store_id=store_id,
        #     warehouse_owner=owner.email,
        #     warehouse_name=self.shop_name,
        #     default=True
        # )

    @staticmethod
    def _create_confirmation_token():
        return secrets.token_urlsafe(64)

    def resend_confirmation_link(self):
        # make new confirmation token
        self.confirmation_token = ShopRegistration._create_confirmation_token()
        self.last_resend = datetime.now()
        self.version += 1

        # add domain event
        self._record_event(ShopRegistrationResendEvent(
            self.registration_id,
            self.shop_name,
            self.owner_email,
            self.confirmation_token
        ))
