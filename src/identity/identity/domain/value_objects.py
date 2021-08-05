#!/usr/bin/env python
# -*- coding: utf-8 -*-
from enum import Enum
from typing import NewType

UserId = NewType('UserId', tp=str)
UserEmail = NewType('UserEmail', tp=str)


class ExceptionMessages(Enum):
    USER_NOT_FOUND = 'User not found'
    PASSWORD_MISMATCH = 'PASSWORD_MISMATCH'
    FAILED_LOGIN_EXCEED = 'Too much failed login'
