#!/usr/bin/env python
# -*- coding: utf-8 -*-
import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import event, UniqueConstraint

from db_infrastructure import metadata, GUID, JsonType
from foundation.database_setup import location_address_table
from identity.adapters.identity_db import user_table
from store.domain.entities.store import Store
from store.domain.entities.store_address import StoreAddressType
from store.domain.entities.store_registration import StoreRegistration
from store.domain.entities.registration_status import RegistrationStatus

store_registration_table = sa.Table(
    'store_registration',
    metadata,
    sa.Column('store_registration_id', GUID, primary_key=True, default=uuid.uuid4),
    sa.Column('name', sa.String(100)),
    sa.Column('owner_email', sa.String(255), unique=True, nullable=False),
    sa.Column('owner_password', sa.String(255), nullable=False),
    sa.Column('owner_mobile', sa.String(255), unique=True),
    sa.Column('confirmation_token', sa.String(200), nullable=False),
    sa.Column('confirmed_at', sa.DateTime),
    sa.Column('status', sa.Enum(RegistrationStatus), nullable=False,
              default=RegistrationStatus.REGISTRATION_WAITING_FOR_CONFIRMATION),
    sa.Column('version', sa.Integer, default='0'),
    sa.Column('last_resend', sa.DateTime),
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
    sa.Column('_owner_id', sa.ForeignKey(store_owner_table.c.id, ondelete='SET NULL', onupdate='CASCADE')),
    sa.Column('owner_email', sa.String(255), nullable=False, comment='For easy linking'),
    sa.Column('disabled', sa.Boolean, default=False, comment='Disabled by admin'),
    sa.Column('version', sa.Integer, nullable=False, default=0),
    sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    sa.Column('last_updated', sa.DateTime, onupdate=datetime.now),
)

store_warehouse_table = sa.Table(
    'warehouse',
    metadata,
    sa.Column('warehouse_id', GUID, primary_key=True),
    sa.Column('store_id', sa.ForeignKey(store_table.c.store_id, onupdate='CASCADE', ondelete='CASCADE')),
    sa.Column('warehouse_owner', sa.String(255), nullable=False, comment='For easy linking'),
    sa.Column('warehouse_name', sa.String(255), nullable=False),
    sa.Column('default', sa.Boolean, default='0'),
    sa.Column('disabled', sa.Boolean, default='0'),
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

store_addresses_table = sa.Table(
    'store_addresses',
    metadata,
    sa.Column('store_address_id', GUID, primary_key=True, default=uuid.uuid4),
    sa.Column('address_id',
              sa.ForeignKey(location_address_table.c.address_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('store_id', sa.ForeignKey(store_table.c.store_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('recipient', sa.String(100), nullable=False),
    sa.Column('phone', sa.String(100)),
    sa.Column('address_type', sa.Enum(StoreAddressType), nullable=False, default=StoreAddressType.STORE_ADDRESS),
    sa.Column('_street_address', sa.String(255)),
    sa.Column('_postal_code', sa.String(255)),
    sa.Column('_sub_division_name', sa.String(255)),
    sa.Column('_division_name', sa.String(255)),
    sa.Column('_city_name', sa.String(255)),
    sa.Column('_country_name', sa.String(255)),
    sa.Column('_iso_code', sa.String(255)),
)

store_catalog_table = sa.Table(
    'store_catalog',
    metadata,
    sa.Column('catalog_id', GUID, primary_key=True, default=uuid.uuid4),
    sa.Column('store_id', sa.ForeignKey(store_table.c.store_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('reference', sa.String(100), nullable=False, unique=True),
    sa.Column('title', sa.String(255), nullable=False),
    sa.Column('image', sa.String(255)),
    sa.Column('default', sa.Boolean, default=False),
    sa.Column('disabled', sa.Boolean, default=False),
    sa.Column('deleted', sa.Boolean, default=False),
    sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),

    UniqueConstraint('store_id', 'reference', name='store_catalog_store_id_reference_ux'),
)

store_collection_table = sa.Table(
    'store_collection',
    metadata,
    sa.Column('collection_id', GUID, primary_key=True, default=uuid.uuid4),
    sa.Column('store_id', sa.ForeignKey(store_table.c.store_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('catalog_id', sa.ForeignKey(store_catalog_table.c.catalog_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('reference', sa.String(100), nullable=False),
    sa.Column('title', sa.String(255), nullable=False),
    sa.Column('default', sa.Boolean, default=False),
    sa.Column('disabled', sa.Boolean, default=False),
    sa.Column('deleted', sa.Boolean, default=False),
    sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),

    # sa.PrimaryKeyConstraint('store_id', 'catalog_id', 'reference', name='store_catalog_collection_pk')
)

# region ## Store Data Value ##
store_brand_table = sa.Table(
    'store_brand',
    metadata,
    # sa.Column('reference', sa.String(100)),
    sa.Column('brand_id', GUID, primary_key=True, default=uuid.uuid4),
    sa.Column('store_id', sa.ForeignKey(store_table.c.store_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('name', sa.String(255), nullable=False),
    sa.Column('logo', sa.String(255), nullable=True, default=''),
    sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
)

store_supplier_table = sa.Table(
    'store_supplier',
    metadata,
    sa.Column('supplier_id', GUID, primary_key=True, default=uuid.uuid4),
    sa.Column('store_id', sa.ForeignKey(store_table.c.store_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('supplier_name', sa.String, nullable=False),
    sa.Column('contact_name', sa.String, nullable=False),
    sa.Column('contact_phone', sa.String, nullable=False),
    sa.Column('disabled', sa.Boolean, server_default='0'),
    sa.Column('deleted', sa.Boolean, server_default='0'),
    sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
)

# endregion

store_product_table = sa.Table(
    'store_product',
    metadata,
    sa.Column('product_id', GUID, primary_key=True, default=uuid.uuid4),
    sa.Column('store_id', sa.ForeignKey(store_table.c.store_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('reference', sa.String(100), nullable=False),
    sa.Column('title', sa.String(255), nullable=False),
    sa.Column('sku', sa.String(100), nullable=False),
    sa.Column('image', sa.String(1000)),
    sa.Column('brand_id', sa.ForeignKey(store_brand_table.c.brand_id), nullable=True),
    sa.Column('catalog_id', sa.ForeignKey(store_catalog_table.c.catalog_id), nullable=True),

    sa.Column('restock_threshold', sa.Integer, default='-1'),
    sa.Column('maxstock_threshold', sa.Integer, default='-1'),

    sa.Column('deleted', sa.Boolean, default=0),
    sa.Column('created_at', sa.DateTime, nullable=False, default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),

    sa.UniqueConstraint('store_id', 'reference', name='store_product_store_id_reference_ux'),
    sa.UniqueConstraint('store_id', 'sku', name='store_product_store_id_sku_ux'),
)

store_product_data_cache_table = sa.Table(
    '__store_product_data_cache',
    metadata,
    sa.Column('product_cache_id',
              sa.ForeignKey(store_product_table.c.product_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('catalog_json', JsonType),
    sa.Column('brand_json', JsonType),
    sa.Column('collections_json', JsonType),
    sa.Column('units_json', JsonType),

    sa.Column('created_at', sa.DateTime, nullable=False, default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),

    sa.PrimaryKeyConstraint('product_cache_id', name='product_cache_pk'),
)

store_product_collection_table = sa.Table(
    'store_product_collection',
    metadata,
    sa.Column('product_id', sa.ForeignKey(store_product_table.c.product_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('collection_id',
              sa.ForeignKey(store_collection_table.c.collection_id, ondelete='CASCADE', onupdate='CASCADE')),

    sa.PrimaryKeyConstraint('product_id', 'collection_id', name='product_collection_pk'),
)

store_product_unit_table = sa.Table(
    'store_product_unit',
    metadata,
    sa.Column('product_id', sa.ForeignKey(store_product_table.c.product_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('unit_name', sa.String(50)),

    sa.UniqueConstraint('product_id', 'unit_name', name='store_product_unit_uix'),
    sa.PrimaryKeyConstraint('product_id', 'unit_name', name='store_product_unit_pk'),

    sa.Column('referenced_unit_name', nullable=True, default=None),
    sa.Column('conversion_factor', sa.Numeric, nullable=True, server_default='1'),

    sa.Column('default', sa.Boolean, default=False, server_default='0'),
    sa.Column('disabled', sa.Boolean, default=False, server_default='0'),
    sa.Column('deleted', sa.Boolean, server_default='0'),

    sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
    sa.Column('last_updated', sa.DateTime, onupdate=datetime.now),

    sa.ForeignKeyConstraint(
        ('product_id', 'referenced_unit_name'),
        ['store_product_unit.product_id', 'store_product_unit.unit_name'],
        name='store_product_unit_fk',
        ondelete='SET NULL'
    ),
)

store_product_supplier_table = sa.Table(
    'store_product_supplier',
    metadata,
    sa.Column('product_id', sa.ForeignKey(store_product_table.c.product_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('supplier_id', sa.ForeignKey(store_supplier_table.c.supplier_id, ondelete='CASCADE', onupdate='CASCADE')),

    sa.PrimaryKeyConstraint('product_id', 'supplier_id', name='product_supplier_pk')
)

store_supplier_product_price_table = sa.Table(
    'store_supplier_product_price',
    metadata,
    sa.Column('product_price_id', GUID, primary_key=True, default=uuid.uuid4),
    sa.Column('product_id', sa.ForeignKey(store_product_table.c.product_id, onupdate='CASCADE', ondelete='CASCADE'),
              nullable=False),
    sa.Column('supplier_id', sa.ForeignKey(store_supplier_table.c.supplier_id, onupdate='CASCADE', ondelete='CASCADE'),
              nullable=False),

    sa.Column('unit', sa.String(50), nullable=False),
    sa.Column('price', sa.Numeric, nullable=False),
    sa.Column('currency', sa.String(10), nullable=False),
    sa.Column('tax', sa.Numeric),
    sa.Column('effective_from', sa.DateTime, nullable=False, server_default=sa.func.now()),

    sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
    sa.Column('last_updated', sa.DateTime, onupdate=datetime.now),

    sa.ForeignKeyConstraint(('product_id', 'unit'),
                            [store_product_unit_table.c.product_id, store_product_unit_table.c.unit_name],
                            name='store_product_unit_fk'),
    sa.UniqueConstraint('product_id', 'supplier_id', 'unit', 'effective_from', name='store_product_supplier_price_uix'),
)

store_unit_cache_table = sa.Table(
    'store_units_cache',
    metadata,
    sa.Column('store_id', sa.ForeignKey(store_table.c.store_id)),
    sa.Column('unit', sa.String(100))
)

store_product_tag_table = sa.Table(
    'store_product_tag',
    metadata,
    # sa.Column('id', GUID, primary_key=True, default=uuid.uuid4),
    sa.Column('product_id', sa.ForeignKey(store_product_table.c.product_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('tag', sa.String(100)),

    sa.PrimaryKeyConstraint('product_id', 'tag', name='store_product_tag_pk'),
    sa.UniqueConstraint('product_id', 'tag', name='product_id_tag_uix'),
)


@event.listens_for(StoreRegistration, 'load')
def store_registration_load(store_registration, _):
    store_registration.domain_events = []


@event.listens_for(Store, 'load')
def store_load(store, connection):
    store.domain_events = []
