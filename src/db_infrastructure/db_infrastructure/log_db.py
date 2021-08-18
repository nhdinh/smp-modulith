#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlalchemy as sa

from db_infrastructure import GUID, metadata

request_log_table = sa.Table(
    'request_log',
    metadata,
    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),  # auto incrementing
    sa.Column('request_id', GUID, nullable=False),
    sa.Column('logger', sa.String(100)),  # the name of the logger. (e.g. myapp.views)
    sa.Column('level', sa.String(100)),  # info, debug, or error?
    sa.Column('trace', sa.String(4096)),  # the full traceback printout
    sa.Column('msg', sa.String(4096)),  # any custom log you may have included
    sa.Column('created_at', sa.DateTime, default=sa.func.now()),  # the current timestamp
)
