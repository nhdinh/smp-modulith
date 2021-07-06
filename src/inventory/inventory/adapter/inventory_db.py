#!/usr/bin/env python
# -*- coding: utf-8 -*-
import uuid
from datetime import datetime

import sqlalchemy as sa

from db_infrastructure import metadata, nanoid_generate
from inventory.domain.entities.purchase_order_status import PurchaseOrderStatus
from store.adapter.store_db import store_product_table, store_product_unit_table, store_supplier_table, \
    store_addresses_table, store_warehouse_table


# inventory_product_table = sa.Table(
#     'store_product',
#     metadata,
#     sa.Column('product_id', GUID, primary_key=True),
#     # sa.Column('store_id', sa.ForeignKey(store_table.c.store_id, ondelete='CASCADE', onupdate='CASCADE')),
#     sa.Column('reference', sa.String(100), nullable=False),
#     sa.Column('title', sa.String(255), nullable=False),
#     sa.Column('sku', sa.String(100), nullable=False),
#     sa.Column('image', sa.String(1000)),
#     # sa.Column('brand_id', sa.ForeignKey(store_brand_table.c.brand_id), nullable=True),
#     # sa.Column('catalog_id', sa.ForeignKey(store_catalog_table.c.catalog_id), nullable=True),
#
#     sa.Column('restock_threshold', sa.Integer, default='-1'),
#     sa.Column('maxstock_threshold', sa.Integer, default='-1'),
#
#     sa.Column('deleted', sa.Boolean, default=0),
#     sa.Column('created_at', sa.DateTime, nullable=False, default=sa.func.now()),
#     sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
#
#     extend_existing=True
# )

# warehouse_table = sa.Table(
#     'warehouse',
#     metadata,
#     sa.Column('warehouse_id', GUID, primary_key=True),
#     sa.Column('store_id', sa.ForeignKey(store_table.c.store_id, onupdate='CASCADE', ondelete='CASCADE')),
#     sa.Column('store_name', sa.String(255)),
#     sa.Column('name', sa.String(255)),
#     sa.Column('disabled', sa.Boolean, default='0'),
#     sa.Column('version', sa.Integer, default='0'),
#
#     sa.Column('created_at', sa.DateTime, nullable=False, default=sa.func.now()),
#     sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
#
#     extend_existing=True
# )

def purchase_order_id_generator():
    return nanoid_generate(prefix='PO', key_size=(20, 10))


draft_purchase_order_table = sa.Table(
    'draft_purchase_order',
    metadata,
    sa.Column('purchase_order_id', sa.String(40), primary_key=True, default=purchase_order_id_generator),
    sa.Column('warehouse_id',
              sa.ForeignKey(store_warehouse_table.c.warehouse_id, onupdate='SET NULL', ondelete='SET NULL')),
    sa.Column('supplier_id',
              sa.ForeignKey(store_supplier_table.c.supplier_id, onupdate='SET NULL', ondelete='SET NULL')),
    sa.Column('store_address_id',
              sa.ForeignKey(store_addresses_table.c.store_address_id, onupdate='SET NULL', ondelete='SET NULL')),
    sa.Column('note', sa.String),
    sa.Column('due_date', sa.Date),
    sa.Column('creator', sa.String(255), nullable=False),
    sa.Column('status', sa.Enum(PurchaseOrderStatus), nullable=False, default=PurchaseOrderStatus.DRAFT),
    sa.Column('version', sa.Integer, nullable=False, default=0),
    sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    sa.Column('last_updated', sa.DateTime, onupdate=datetime.now),
)


def purchase_order_item_id_generator():
    return nanoid_generate(prefix='POI')


draft_purchase_order_item_table = sa.Table(
    'draft_purchase_order_item',
    metadata,
    sa.Column('purchase_order_item_id', sa.String(40), primary_key=True, default=purchase_order_item_id_generator),
    sa.Column('purchase_order_id',
              sa.ForeignKey(draft_purchase_order_table.c.purchase_order_id, onupdate='CASCADE', ondelete='CASCADE')),
    sa.Column('product_id', sa.ForeignKey(store_product_table.c.product_id)),
    sa.Column('unit_unit', sa.String(50), nullable=False),
    sa.Column('quantity', sa.Numeric, default=1, nullable=False),
    sa.Column('description', sa.String(255)),

    sa.UniqueConstraint('purchase_order_id', 'product_id', 'unit_unit', name='draft_purchase_order_product_unit_uix'),
    sa.ForeignKeyConstraint(('product_id', 'unit_unit'),
                            [store_product_unit_table.c.product_id, store_product_unit_table.c.unit_name],
                            name='draft_purchase_order_product_fk', ondelete='SET NULL')
)

inventory_product_balance_table = sa.Table(
    'inventory_balance',
    metadata,
    sa.Column('product_id', sa.String),
    sa.Column('unit', sa.String(50), nullable=False),

    sa.Column('stocking_quantity', sa.Integer, default='0'),

    sa.Column('created_at', sa.DateTime, nullable=False, default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),

    sa.ForeignKeyConstraint(('product_id', 'unit'),
                            [store_product_unit_table.c.product_id, store_product_unit_table.c.unit_name],
                            name='inventory_balance_product_unit_pk', ondelete='SET NULL')
)
