#!/usr/bin/env python
# -*- coding: utf-8 -*-
import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import event

from db_infrastructure import metadata, GUID
from identity.adapters.identity_db import user_table
from store.domain.entities.store import Store
from store.domain.entities.store_catalog import StoreCatalog
from store.domain.entities.store_registration import StoreRegistration

store_registration_table = sa.Table(
    'store_registration',
    metadata,
    sa.Column('store_registration_id', GUID, primary_key=True),
    sa.Column('name', sa.String(100)),
    sa.Column('owner_email', sa.String(255), unique=True, nullable=False),
    sa.Column('owner_password', sa.String(255), nullable=False),
    sa.Column('owner_mobile', sa.String(255), unique=True),
    sa.Column('confirmation_token', sa.String(200), nullable=False),
    sa.Column('confirmed_at', sa.DateTime),
    sa.Column('status', sa.String(100), nullable=False, default='new_registration'),
    sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
)

store_owner_table = sa.Table(
    'user',
    metadata,
    sa.Column('id', GUID, primary_key=True),
    sa.Column('email', sa.String(255), unique=True),
    sa.Column('mobile', sa.String(255), unique=True),
    sa.Column('password', sa.String(255)),
    sa.Column('active', sa.Boolean),
    sa.Column('confirmed_at', sa.DateTime),

    extend_existing=True
)  # extend of user table

store_table = sa.Table(
    'store',
    metadata,
    sa.Column('store_id', GUID, primary_key=True),
    sa.Column('name', sa.String(100)),
    sa.Column('owner', sa.ForeignKey(store_owner_table.c.id, ondelete='SET NULL', onupdate='CASCADE')),
    sa.Column('owner_email', sa.String(255), comment='For easy linking'),
    sa.Column('disabled', sa.Boolean, default=False, comment='Disabled by admin'),
    sa.Column('version', GUID, nullable=False, default=uuid.uuid4),
    sa.Column('version', sa.Integer, nullable=False, default=0),
    sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    sa.Column('last_updated', sa.DateTime, onupdate=datetime.now),
)

store_settings_table = sa.Table(
    'store_settings',
    metadata,
    sa.Column('store_id', sa.ForeignKey(store_table.c.store_id, ondelete='CASCADE', onupdate='CASCADE'),
              primary_key=True),
    sa.Column('setting_key', sa.String(100), nullable=False, primary_key=True),
    sa.Column('setting_value', sa.String(100), nullable=False),
    sa.Column('setting_type', sa.String(100), nullable=False),
    sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    sa.Column('last_updated', sa.DateTime, onupdate=datetime.now),
)

store_managers_table = sa.Table(
    'store_managers',
    metadata,
    sa.Column('store_id', sa.ForeignKey(store_table.c.store_id, ondelete='SET NULL', onupdate='CASCADE')),
    sa.Column('user_id', sa.ForeignKey(user_table.c.id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('store_role_id', sa.String(100), default='store_manager'),
)

store_address_table = sa.Table(
    'store_addresses',
    metadata,
    sa.Column('address_id', GUID, primary_key=True),
    sa.Column('store_id', sa.ForeignKey(store_table.c.store_id, ondelete='CASCADE', onupdate='CASCADE')),
)

store_catalog_table = sa.Table(
    'store_catalog',
    metadata,
    sa.Column('catalog_id', GUID, primary_key=True),
    sa.Column('store_id', sa.ForeignKey(store_table.c.store_id, ondelete='CASCADE', onupdate='CASCADE')),
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
    sa.Column('store_id', sa.ForeignKey(store_table.c.store_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('catalog_id', sa.ForeignKey(store_catalog_table.c.catalog_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('reference', sa.String(100), nullable=False),
    sa.Column('display_name', sa.String(255), nullable=False),
    sa.Column('default', sa.Boolean, default=False),
    sa.Column('disabled', sa.Boolean, default=False),
    sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
)

store_product_table = sa.Table(
    'store_product',
    metadata,
    sa.Column('product_id', GUID, primary_key=True),
    sa.Column('collection_id',
              sa.ForeignKey(store_collection_table.c.collection_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('reference', sa.String(100), nullable=False),
    sa.Column('display_name', sa.String(255), nullable=False),
)

store_catalog_cache_table = sa.Table(
    'store_catalogs_cache',
    metadata,
    sa.Column('store_id', sa.ForeignKey(store_table.c.store_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('catalog_id', sa.ForeignKey(store_catalog_table.c.catalog_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('catalog_reference', sa.String(100))
)

store_collection_cache_table = sa.Table(
    'store_collection_cache',
    metadata,
    sa.Column('store_id', sa.ForeignKey(store_table.c.store_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('catalog_id', sa.ForeignKey(store_catalog_table.c.catalog_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('collection_id',
              sa.ForeignKey(store_collection_table.c.collection_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('collection_reference', sa.String(100))
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

# region ## Store Data Value ##
store_brand_table = sa.Table(
    'store_brand',
    metadata,
    sa.Column('reference', sa.String(100), primary_key=True),
    sa.Column('store_id', sa.ForeignKey(store_table.c.store_id, ondelete='CASCADE', onupdate='CASCADE'),
              primary_key=True),
    sa.Column('display_name', sa.String(255), nullable=False)
)

store_product_brands_table = sa.Table(
    'store_product_brands',
    metadata,
    sa.Column('product_id', sa.ForeignKey(store_product_table.c.product_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('store_id', GUID, nullable=False),
    sa.Column('brand_reference', sa.String(100), nullable=False),

    sa.ForeignKeyConstraint(('store_id', 'brand_reference'),
                            [store_brand_table.c.store_id, store_brand_table.c.reference])
)


# endregion


@event.listens_for(StoreRegistration, 'load')
def store_registration_load(store_registration, _):
    store_registration.domain_events = []


@event.listens_for(Store, 'load')
def store_load(store, connection):
    store.domain_events = []
    store._cached = {
        'catalogs': [],
        'collections': [],
        'products': []
    }

    # fetch cache of catalogs into the store
    q = sa.select([store_catalog_table.c.reference, store_catalog_table.c.catalog_id]).where(
        store_catalog_table.c.store_id == store.store_id)
    fetched_catalogs = connection.session.execute(q).all()
    store._cached['catalogs'] = [r.reference for r in fetched_catalogs]
    _catalog_indice = [r.catalog_id for r in fetched_catalogs]

    # fetch cache of collections into the store
    q = sa.select([store_collection_table.c.reference, store_collection_table.c.collection_id]).where(
        store_collection_cache_table.c.catalog_id.in_(_catalog_indice)
    )
    fetched_collections = connection.session.execute(q).all()
    store._cached['collections'] = [r.reference for r in fetched_collections]


@event.listens_for(StoreCatalog, 'load')
def ctalog_load(catalog, connection):
    catalog._cached = {
        'collection': [],
        'products': []
    }

    # fetch cache of collections into the store
    q = sa.select([store_collection_cache_table.c.collection_reference]).where(
        store_collection_cache_table.c.store_id == catalog.store_id).where(
        store_collection_cache_table.c.catalog_id == catalog.catalog_id
    )

    fetched_collections = connection.session.execute(q).all()
    catalog._cached['collections'] = [r.collection_reference for r in fetched_collections]
