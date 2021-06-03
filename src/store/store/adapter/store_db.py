#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import Table, Column, String, ForeignKey, func, DateTime
from sqlalchemy.orm import mapper, relationship

from db_infrastructure import metadata, GUID
from identity.adapters.identity_db import user_table
from store.domain.entities.setting import Setting
from store.domain.entities.store import Store

store_table = Table(
    'store',
    metadata,
    Column('store_id', GUID, primary_key=True),
    Column('name', String(100)),
    Column('owner', ForeignKey(user_table.c.id)),
    Column('created_at', DateTime, server_default=func.now()),
    Column('last_updated', DateTime, onupdate=datetime.now),
)

store_settings_table = Table(
    'store_settings',
    metadata,
    Column('setting_id', GUID, primary_key=True),
    Column('store_id', ForeignKey(store_table.c.store_id)),
    Column('setting_name', String(100), nullable=False),
    Column('setting_value', String(100), nullable=False),
    Column('setting_type', String(100), nullable=False),
    Column('created_at', DateTime, server_default=func.now()),
    Column('last_updated', DateTime, onupdate=datetime.now),
)

store_managers_table = Table(
    'store_managers',
    metadata,
    Column('store_id', ForeignKey(store_table.c.store_id)),
    Column('user_id', ForeignKey(user_table.c.id)),
    Column('store_role_id', String(100), default='store_manager'),
)

store_address_table = Table(
    'store_addresses',
    metadata,
    Column('address_id', GUID, primary_key=True),
    Column('store_id', ForeignKey(store_table.c.store_id))
)


def start_mappers():
    mapper(
        Setting,
        store_settings_table,
    )

    store_mapper = mapper(
        Store,
        store_table,

        properties={
            '_settings': relationship(
                Setting,
                collection_class=set
            ),
            '_owner': relationship(
                user_table
            ),
            '_managers': relationship(
                store_managers_table,
                collection_class=set,
            )
        }
    )
