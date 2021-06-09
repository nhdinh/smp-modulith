#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import Table, Column, String, ForeignKey, func, DateTime, event, Boolean

from db_infrastructure import metadata, GUID
from identity.adapters.identity_db import user_table
from store.domain.entities.store import Store
from store.domain.entities.store_registration import StoreRegistration

store_registration_table = Table(
    'store_registration',
    metadata,
    Column('store_registration_id', GUID, primary_key=True),
    Column('name', String(100)),
    Column('owner_email', String(255), unique=True, nullable=False),
    Column('owner_password', String(255), nullable=False),
    Column('owner_mobile', String(255), unique=True),
    Column('confirmation_token', String(200), nullable=False),
    Column('confirmed_at', DateTime),
    Column('status', String(100), nullable=False, default='new_registration'),
    Column('created_at', DateTime, server_default=func.now()),
)

store_owner_table = Table(
    'user',
    metadata,
    Column('id', GUID, primary_key=True),
    Column('email', String(255), unique=True),
    Column('mobile', String(255), unique=True),
    Column('password', String(255)),
    Column('active', Boolean),
    Column('confirmed_at', DateTime),

    extend_existing=True
)  # extend of user table

store_table = Table(
    'store',
    metadata,
    Column('store_id', GUID, primary_key=True),
    Column('name', String(100)),
    Column('owner', ForeignKey(store_owner_table.c.id)),
    Column('created_at', DateTime, server_default=func.now()),
    Column('last_updated', DateTime, onupdate=datetime.now),
)

store_settings_table = Table(
    'store_settings',
    metadata,
    Column('store_id', ForeignKey(store_table.c.store_id), primary_key=True),
    Column('setting_name', String(100), nullable=False, primary_key=True),
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
    Column('store_id', ForeignKey(store_table.c.store_id)),
)


@event.listens_for(StoreRegistration, 'load')
def store_registration_load(store_registration, _):
    store_registration.domain_events = []
