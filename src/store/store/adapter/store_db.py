#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import Table, Column, String, ForeignKey, func, DateTime, event
from sqlalchemy.orm import mapper, relationship, backref

from db_infrastructure import metadata, GUID
from identity.adapters.identity_db import user_table
from identity.domain.entities import User
from store.domain.entities.setting import Setting
from store.domain.entities.store import Store
from store.domain.entities.store_owner import StoreOwner
from store.domain.entities.store_registration import StoreRegistration

store_registration_table = Table(
    'store_registration',
    metadata,
    Column('store_registration_id', GUID, primary_key=True),
    Column('name', String(100)),
    Column('owner_email', String(255), unique=True, nullable=False),
    Column('owner_password', String(255), nullable=False),
    Column('owner_mobile', String(255)),
    Column('confirmation_token', String(200), nullable=False),
    Column('status', String(100), nullable=False, default='new_registration'),
    Column('created_at', DateTime, server_default=func.now()),
)

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

store_owner_table = Table(
    'user',
    metadata,
    Column('email', String(255), unique=True),
    extend_existing=True
)  # extend of user table

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
    Column('store_id', ForeignKey(store_table.c.store_id)),
)


def start_mappers():
    mapper(
        Setting,
        store_settings_table,
    )

    mapper(
        StoreRegistration,
        store_registration_table,
        properties={
            'registration_id': store_registration_table.c.store_registration_id,
            'store_name': store_registration_table.c.name,
        }
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
                User,
                user_table,
                foreigns_key=['owner'],
            ),
            '_managers': relationship(
                User,
                secondary=store_managers_table,
                collection_class=set,
            )
        }
    )

    owner = mapper(
        StoreOwner,
        store_owner_table,
        properties={
            '_store': relationship(
                Store,
                backref=backref('_owner')
            )
        }
    )


@event.listens_for(StoreRegistration, 'load')
def store_registration_load(store_registration, _):
    store_registration._pending_domain_events = []
