#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime

import sqlalchemy as sa

from db_infrastructure import JsonType, metadata
from db_infrastructure.mt import GUID
from foundation.database_setup import location_address_table
from foundation.events import EventStatus
from shop.adapter.id_generators import (
    generate_brand_id,
    generate_product_id,
    generate_product_purchase_price_id,
    generate_shop_address_id,
    generate_shop_catalog_id,
    generate_shop_collection_id,
    generate_shop_id,
    generate_supplier_id,
)
from shop.domain.entities.value_objects import AddressType, RegistrationStatus, GenericShopItemStatus, ShopStatus, \
    ShopUserType

shop_registration_table = sa.Table(
    'shop_registration',
    metadata,
    sa.Column('shop_registration_id', sa.String(40), primary_key=True, default=generate_shop_id),
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
    sa.Column('updated_at', sa.DateTime, onupdate=datetime.now),
)

shop_table = sa.Table(
    'shop',
    metadata,
    sa.Column('shop_id', sa.String(40), primary_key=True, default=generate_shop_id),
    sa.Column('name', sa.String(100)),
    sa.Column('status', sa.Enum(ShopStatus), nullable=False, default=ShopStatus.NORMAL),
    sa.Column('version', sa.Integer, nullable=False, default=0),
    sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, onupdate=datetime.now),
)

shop_warehouse_table = sa.Table(
    'shop_warehouse',
    metadata,
    sa.Column('warehouse_id', sa.String(40), nullable=False, primary_key=True),
    sa.Column('shop_id', sa.ForeignKey(shop_table.c.shop_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('warehouse_name', sa.String(100)),
)

shop_users_table = sa.Table(
    'shop_user',
    metadata,
    sa.Column('shop_id', sa.ForeignKey(shop_table.c.shop_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('user_id', sa.String(40), unique=True),
    sa.Column('email', sa.String(255)),
    sa.Column('mobile', sa.String(100), unique=True),
    sa.Column('shop_role', sa.Enum(ShopUserType), default=ShopUserType.MANAGER),
    sa.Column('status', sa.Enum(GenericShopItemStatus), nullable=False, default=GenericShopItemStatus.NORMAL),
    sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, onupdate=datetime.now),

    sa.PrimaryKeyConstraint('shop_id', 'user_id', name='shop_users_pk'),
)

shop_settings_table = sa.Table(
    'shop_settings',
    metadata,
    sa.Column('shop_id', sa.ForeignKey(shop_table.c.shop_id, ondelete='CASCADE', onupdate='CASCADE'),
              primary_key=True),
    sa.Column('setting_key', sa.String(100), nullable=False, primary_key=True),
    sa.Column('setting_value', sa.String(100), nullable=False),
    sa.Column('setting_type', sa.String(100), nullable=False),
    sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, onupdate=datetime.now),

    sa.PrimaryKeyConstraint('shop_id', 'setting_key', name='shop_id_settings_key_pk'),
)

shop_addresses_table = sa.Table(
    'shop_addresses',
    metadata,
    sa.Column('shop_address_id', sa.String(40), primary_key=True, default=generate_shop_address_id),
    sa.Column('address_id',
              sa.ForeignKey(location_address_table.c.address_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('shop_id', sa.ForeignKey(shop_table.c.shop_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('recipient', sa.String(100), nullable=False),
    sa.Column('phone', sa.String(100)),
    sa.Column('address_type', sa.Enum(AddressType), nullable=False, default=AddressType.SHOP_ADDRESS),
    sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
)

shop_catalog_table = sa.Table(
    'shop_catalog',
    metadata,
    sa.Column('catalog_id', sa.String(40), primary_key=True, default=generate_shop_catalog_id),
    sa.Column('shop_id', sa.ForeignKey(shop_table.c.shop_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('title', sa.String(255), nullable=False),
    sa.Column('image', sa.String(255)),
    sa.Column('default', sa.Boolean, default=False),
    sa.Column('status', sa.Enum(GenericShopItemStatus), nullable=False, default=GenericShopItemStatus.NORMAL),
    sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
)

shop_collection_table = sa.Table(
    'shop_collection',
    metadata,
    sa.Column('collection_id', sa.String(40), primary_key=True, default=generate_shop_collection_id),
    sa.Column('shop_id', sa.ForeignKey(shop_table.c.shop_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('catalog_id', sa.ForeignKey(shop_catalog_table.c.catalog_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('title', sa.String(255), nullable=False),
    sa.Column('default', sa.Boolean, default=False),
    sa.Column('status', sa.Enum(GenericShopItemStatus), nullable=False, default=GenericShopItemStatus.NORMAL),
    sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
)

# region ## Shop Data Value ##


shop_brand_table = sa.Table(
    'shop_brand',
    metadata,
    # sa.Column('reference', sa.String(100)),
    sa.Column('brand_id', sa.String(40), primary_key=True, default=generate_brand_id),
    sa.Column('shop_id', sa.ForeignKey(shop_table.c.shop_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('name', sa.String(255), nullable=False),
    sa.Column('logo', sa.String(255), nullable=True, default=''),
    sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
)

shop_supplier_table = sa.Table(
    'shop_supplier',
    metadata,
    sa.Column('supplier_id', sa.String(40), primary_key=True, unique=True, default=generate_supplier_id),
    sa.Column('shop_id', sa.ForeignKey(shop_table.c.shop_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('supplier_name', sa.String, nullable=False),
    sa.Column('status', sa.Enum(GenericShopItemStatus), nullable=False, default=GenericShopItemStatus.NORMAL),
    sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
)

shop_supplier_contact_table = sa.Table(
    'shop_supplier_contact',
    metadata,
    sa.Column('supplier_id', sa.ForeignKey(shop_supplier_table.c.supplier_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('contact_name', sa.String, nullable=False),
    sa.Column('contact_phone', sa.String, nullable=False),
    sa.Column('status', sa.Enum(GenericShopItemStatus), nullable=False, default=GenericShopItemStatus.NORMAL),
    sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),

    sa.PrimaryKeyConstraint('supplier_id', 'contact_name', 'contact_phone', name='shop_supplier_contact_pk'),
)

# endregion


shop_product_table = sa.Table(
    'shop_product',
    metadata,
    sa.Column('product_id', sa.String(40), primary_key=True, default=generate_product_id),
    sa.Column('shop_id', sa.ForeignKey(shop_table.c.shop_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('title', sa.String(255), nullable=False),
    sa.Column('sku', sa.String(100), nullable=False),
    sa.Column('barcode', sa.String(100), nullable=False),
    sa.Column('image', sa.String(1000)),
    sa.Column('brand_id', sa.ForeignKey(shop_brand_table.c.brand_id), nullable=True),
    sa.Column('catalog_id', sa.ForeignKey(shop_catalog_table.c.catalog_id), nullable=True),

    sa.Column('restock_threshold', sa.Integer, default='-1'),
    sa.Column('max_stock_threshold', sa.Integer, default='-1'),

    sa.Column('current_stock', sa.Integer, default='0'),

    sa.Column('status', sa.Enum(GenericShopItemStatus), nullable=False, default=GenericShopItemStatus.NORMAL),
    sa.Column('version', sa.Integer, default=0),
    sa.Column('created_at', sa.DateTime, nullable=False, default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),

    sa.UniqueConstraint('shop_id', 'sku', name='shop_product_shop_id_sku_ux'),
)

shop_product_view_cache_table = sa.Table(
    '__shop_product_view_cache',
    metadata,
    sa.Column('product_cache_id',
              sa.ForeignKey(shop_product_table.c.product_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('shop_id', sa.String(40)),
    sa.Column('catalog_id', sa.String(40)),
    sa.Column('brand_id', sa.String(40)),
    sa.Column('catalog_json', JsonType),
    sa.Column('brand_json', JsonType),
    sa.Column('collections_json', JsonType),
    sa.Column('units_json', JsonType),
    sa.Column('suppliers_json', JsonType),
    sa.Column('status', sa.String(20)),

    sa.Column('created_at', sa.DateTime, nullable=False, default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, server_onupdate=sa.func.now()),

    sa.PrimaryKeyConstraint('product_cache_id', name='product_cache_pk'),
)

shop_product_collection_table = sa.Table(
    'shop_product_collection',
    metadata,
    sa.Column('product_id', sa.ForeignKey(shop_product_table.c.product_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('collection_id',
              sa.ForeignKey(shop_collection_table.c.collection_id, ondelete='CASCADE', onupdate='CASCADE')),

    sa.PrimaryKeyConstraint('product_id', 'collection_id', name='product_collection_pk'),
)

shop_product_unit_table = sa.Table(
    'shop_product_unit',
    metadata,
    sa.Column('product_id', sa.ForeignKey(shop_product_table.c.product_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('unit_name', sa.String(50)),

    sa.UniqueConstraint('product_id', 'unit_name', name='shop_product_unit_uix'),
    sa.PrimaryKeyConstraint('product_id', 'unit_name', name='shop_product_unit_pk'),

    sa.Column('referenced_unit_name', nullable=True, default=None),
    sa.Column('conversion_factor', sa.Numeric, nullable=True, server_default='1'),

    sa.Column('default', sa.Boolean, default=False, server_default='0'),
    sa.Column('status', sa.Enum(GenericShopItemStatus), nullable=False, default=GenericShopItemStatus.NORMAL),

    sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, onupdate=datetime.now),

    sa.ForeignKeyConstraint(
        ('product_id', 'referenced_unit_name'),
        ['shop_product_unit.product_id', 'shop_product_unit.unit_name'],
        name='shop_product_unit_fk',
        ondelete='SET NULL'
    ),
)

shop_product_supplier_table = sa.Table(
    'shop_product_supplier',
    metadata,
    sa.Column('product_id', sa.ForeignKey(shop_product_table.c.product_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('supplier_id', sa.ForeignKey(shop_supplier_table.c.supplier_id, ondelete='CASCADE', onupdate='CASCADE')),

    sa.PrimaryKeyConstraint('product_id', 'supplier_id', name='product_supplier_pk')
)

shop_product_purchase_price_table = sa.Table(
    'shop_supplier_product_price',
    metadata,
    sa.Column('product_price_id', sa.String(40), primary_key=True, default=generate_product_purchase_price_id),
    sa.Column('product_id', sa.ForeignKey(shop_product_table.c.product_id, onupdate='CASCADE', ondelete='CASCADE'),
              nullable=False),
    sa.Column('supplier_id', sa.ForeignKey(shop_supplier_table.c.supplier_id, onupdate='CASCADE', ondelete='CASCADE'),
              nullable=False),

    sa.Column('unit', sa.String(50), nullable=False),
    sa.Column('price', sa.Numeric, nullable=False),
    sa.Column('currency', sa.String(10), nullable=False),
    sa.Column('tax', sa.Numeric, nullable=True),
    sa.Column('effective_from', sa.Date, nullable=False, server_default=sa.func.now()),

    sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, onupdate=datetime.now),

    sa.ForeignKeyConstraint(('product_id', 'unit'),
                            [shop_product_unit_table.c.product_id, shop_product_unit_table.c.unit_name],
                            name='shop_product_unit_fk'),
    sa.UniqueConstraint('product_id', 'supplier_id', 'unit', 'effective_from', name='shop_product_supplier_price_uix'),
)

shop_unit_cache_table = sa.Table(
    'shop_units_cache',
    metadata,
    sa.Column('shop_id', sa.ForeignKey(shop_table.c.shop_id)),
    sa.Column('unit', sa.String(100))
)

shop_product_tag_table = sa.Table(
    'shop_product_tag',
    metadata,
    sa.Column('product_id', sa.ForeignKey(shop_product_table.c.product_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('tag', sa.String(100)),

    sa.PrimaryKeyConstraint('product_id', 'tag', name='shop_product_tag_pk'),
    sa.UniqueConstraint('product_id', 'tag', name='product_id_tag_uix'),
)

shop_event_table = sa.Table(
    'shop_events',
    metadata,
    sa.Column('event_id', GUID, primary_key=True),
    sa.Column('event_data', JsonType, nullable=False),
    sa.Column('result_data', JsonType, nullable=True),
    sa.Column('failed_count', sa.Integer, default=0),
    sa.Column('status', sa.Enum(EventStatus), default=EventStatus.PENDING),
    sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, onupdate=datetime.now),

    # TODO: Added destination columns
)
