#!/usr/bin/env python
# -*- coding: utf-8 -*-
import string
from dataclasses import dataclass
from datetime import datetime

import factory
import nanoid
from store.application.usecases.initialize.register_shop_uc import RegisteringShopRequest
from store.domain.entities.shop_registration import ShopRegistrationId
from store.domain.entities.value_objects import ShopId


@dataclass
class CreatedShopRegistration:
  email: str
  password: str
  registration_id: ShopRegistrationId
  confirmation_token: str


@dataclass
class CreatedShopAndAccount:
  email: str
  password: str
  # user_id: UserId
  shop_id: ShopId


class RegisteringShopRequestFactory(factory.Factory):
  class Meta:
    model = RegisteringShopRequest

  name = factory.Faker('name')
  email = factory.Faker('email')
  mobile = factory.LazyFunction(lambda: '+849' + nanoid.generate(string.digits, 8))
  password = factory.LazyFunction(
    lambda: nanoid.generate(string.ascii_letters + string.digits + string.punctuation, 15)
  )
  timestamp = datetime.now().timestamp()
