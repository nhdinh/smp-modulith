#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Table, Column, String, ForeignKey, DateTime, Boolean

from db_infrastructure import metadata, GUID

collection_table = Table(
    'collection',
    metadata,
    Column('reference', String(100), primary_key=True),
    Column('display_name', String(255), nullable=False),
    Column('disabled', Boolean, default=0, server_default='0')
)

catalog_table = Table(
    'catalog',
    metadata,
    Column('id', GUID, primary_key=True),
    Column('reference', String(100), unique=True, nullable=False),
    Column('display_name', String(255), nullable=False),
    Column('default_collection', ForeignKey(collection_table.c.reference)),
    Column('disabled', Boolean, default=0, server_default='0'),
    Column('created_at', DateTime),
)

product_table = Table(
    'product',
    metadata,
    Column('id', GUID, primary_key=True)
)
