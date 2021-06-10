#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
import sqlalchemy as sa

from sqlalchemy import Table, Column, String, ForeignKey, func, DateTime, event, Boolean, select

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
    Column('setting_key', String(100), nullable=False, primary_key=True),
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

store_catalog_table = sa.Table(
    'store_catalog',
    metadata,
    sa.Column('catalog_id', GUID, primary_key=True),
    sa.Column('store_id', sa.ForeignKey(store_table.c.store_id)),
    sa.Column('reference', sa.String(100), nullable=False),
    sa.Column('display_name', sa.String(255), nullable=False),
    sa.Column('display_image', sa.String(255)),
    sa.Column('system', sa.Boolean, default=False),
    sa.Column('disabled', sa.Boolean, default=False),
    sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),

    # sa.PrimaryKeyConstraint(['store_id', 'reference'], name='store_catalog_pk')
)

store_collection_table = sa.Table(
    'store_collection',
    metadata,
    sa.Column('collection_id', GUID, primary_key=True),
    sa.Column('store_id', sa.ForeignKey(store_catalog_table.c.catalog_id)),
    sa.Column('reference', sa.String(100), nullable=False),
    sa.Column('display_name', sa.String(255), nullable=False),
    sa.Column('default', sa.Boolean, default=False),
    sa.Column('disabled', sa.Boolean, default=False),
    sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
)

store_catalog_cache_table = sa.Table(
    'store_catalogs_cache',
    metadata,
    sa.Column('store_id', sa.ForeignKey(store_table.c.store_id)),
    sa.Column('catalog_id', sa.ForeignKey(store_catalog_table.c.catalog_id)),
    sa.Column('catalog_reference', sa.ForeignKey(store_catalog_table.c.reference))
)

store_collection_cache_table = sa.Table(
    'store_collection_cache',
    metadata,
    sa.Column('store_id', sa.ForeignKey(store_table.c.store_id)),
    sa.Column('catalog_id', sa.ForeignKey(store_catalog_table.c.catalog_id)),
    sa.Column('collection_id', sa.ForeignKey(store_collection_table.c.collection_id)),
    sa.Column('collection_reference', sa.ForeignKey(store_collection_table.c.reference))
)


# store_product_cache_table = sa.Table(
#     'store_product_cache',
#     metadata,
#     metadata,
#     sa.Column('store_id', sa.ForeignKey(store_table.c.store_id)),
#     sa.Column('catalog_id', sa.ForeignKey(store_catalog_table.c.catalog_id)),
#     sa.Column('collection_id', sa.ForeignKey(store_collection_table.c.collection_id)),
#     sa.Column('product_id', sa.ForeignKey(store_product_table.c.product_id)),
#     sa.Column('product_reference', sa.String(255))
# )


@event.listens_for(StoreRegistration, 'load')
def store_registration_load(store_registration, _):
    store_registration.domain_events = []


@event.listens_for(Store, 'load')
def store_load(store, connection):
    store.domain_events = []
    store.__cached = {
        'catalogs': [],
        'collections': [],
        'products': []
    }

    # fetch cache of catalogs into the store
    q = select([store_catalog_cache_table.c.catalog_reference]).where(
        store_catalog_cache_table.c.store_id == store.store_id)
    fetched_catalogs = connection.session.execute(q).all()
    store.__cached['catalogs'] = [r.catalog_reference for r in fetched_catalogs]

    # fetch cache of collectons into the store
    q = select([store_collection_cache_table.c.collection_reference]).where(
        store_collection_cache_table.c.store_id == store.store_id)
    fetched_collections = connection.session.execute(q).all()
    store.__cached['collections'] = [r.collection_reference for r in fetched_collections]
