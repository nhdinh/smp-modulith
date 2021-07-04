#!/usr/bin/env python
# -*- coding: utf-8 -*-
from enum import Enum


class RegistrationStatus(Enum):
    REGISTRATION_CONFIRMED = 'Confirmed'
    REGISTRATION_EXPIRED = 'Expired'
    REGISTRATION_WAITING_FOR_CONFIRMATION = 'WaitingForConfirmation'