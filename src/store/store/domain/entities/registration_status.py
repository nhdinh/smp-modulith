#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass


@dataclass(unsafe_hash=True)
class UserRegistrationStatus:
    def __init__(self, value: str):
        super().__init__()
        self._value = value.strip()

    @property
    def value(self):
        return self._value


RegistrationConfirmed = UserRegistrationStatus('Confirmed')
RegistrationExpired = UserRegistrationStatus('Expired')
RegistrationWaitingForConfirmation = UserRegistrationStatus('WaitingForConfirmation')
