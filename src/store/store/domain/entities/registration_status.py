#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from store.domain.entities.value_objects import RegistrationStatus

RegistrationConfirmed = RegistrationStatus('Confirmed')
RegistrationExpired = RegistrationStatus('Expired')
RegistrationWaitingForConfirmation = RegistrationStatus('WaitingForConfirmation')
