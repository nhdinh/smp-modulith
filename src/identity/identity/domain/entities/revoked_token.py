#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import datetime

# from identity.application.queries.identity import CountRevokedTokenByJTIQuery


@dataclass
class RevokedToken:
    jti: str
    revoked_on: datetime = datetime.now()

    @staticmethod
    def is_jti_blacklisted(jti):
        # call something to return the data
        # result = query.query(jti=jti)
        # return bool(result)

        return False
