#!/usr/bin/env python
# -*- coding: utf-8 -*-
from enum import Enum


class RegistrationStatus(Enum):
    REGISTRATION_WAITING_FOR_CONFIRMATION = 'RegistrationWaitingForConfirmation'
    REGISTRATION_CONFIRMED_YET_COMPLETED = 'ConfirmedButYetCompleted'
    REGISTRATION_CONFIRMED_COMPLETED = 'ConfirmedAndCreated'
    REGISTRATION_EXPIRED = 'Expired'
