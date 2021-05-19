#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import datetime


@dataclass
class RevokedToken:
    jti: str
    revoked_on: datetime = datetime.now()

    @staticmethod
    def is_jti_blacklisted(jti):
        return False
