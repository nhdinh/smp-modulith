#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass


@dataclass(unsafe_hash=True)
class RegistrationStatus:
    value: str


RegistrationConfirmed = RegistrationStatus('Confirmed')
RegistrationExpired = RegistrationStatus('Expired')
RegistrationWaitingForConfirmation = RegistrationStatus('WaitingForConfirmation')
