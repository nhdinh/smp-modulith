#!/usr/bin/env python
# -*- coding: utf-8 -*-

from store.domain.entities.value_objects import RegistrationStatus

RegistrationConfirmed = RegistrationStatus('Confirmed')
RegistrationExpired = RegistrationStatus('Expired')
RegistrationWaitingForConfirmation = RegistrationStatus('WaitingForConfirmation')
