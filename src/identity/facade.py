#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy.engine import Connection


class IdentityModuleFacade:
    def __init__(self, config, connection: Connection):
        self._connection = connection

    def create_user(self, dto):
        ...
