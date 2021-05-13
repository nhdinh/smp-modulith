#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

import factory


@dataclass
class CreatingUserRequest:
    email: str
    password: str


class CreatingUserRequestFactory(factory.Factory):
    class Meta:
        model = CreatingUserRequest

    email = factory.Faker('email')
    password = 'Abc123@'
