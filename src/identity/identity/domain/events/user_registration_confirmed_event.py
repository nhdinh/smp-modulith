#!/usr/bin/env python
# -*- coding: utf-8 -*-
from foundation.events import Event


class UserRegistrationConfirmedEvent(Event):
    email: str
    hashed_password: str
