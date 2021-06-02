#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Table, Column, String, ForeignKey
from sqlalchemy.orm import mapper, relationship

from db_infrastructure import metadata, GUID
from store.domain.entities.setting import Setting
from store.domain.entities.store import Store

store_table = Table(
    'store',
    metadata,
    Column('store_id', GUID, primary_key=True),
    Column('name', String(100)),
)

store_settings_table = Table(
    'store_settings',
    metadata,
    Column('setting_id', GUID, primary_key=True),
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
            )
        }
    )
