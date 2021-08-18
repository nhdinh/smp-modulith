#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

import factory

from identity.application.usecases.log_user_in_uc import LoggingUserInRequest


@dataclass
class CreatingUserRequest:
  email: str
  password: str


class CreatingUserRequestFactory(factory.Factory):
  class Meta:
    model = CreatingUserRequest

  email = factory.Faker('email')
  password = 'Abc123@'


class CreatingLoginRequestFactory(factory.Factory):
  class Meta:
    model = LoggingUserInRequest

  username = factory.Faker('email')
  password = 'Abc123@'
