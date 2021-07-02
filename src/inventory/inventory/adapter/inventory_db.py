#!/usr/bin/env python
# -*- coding: utf-8 -*-
import uuid
from datetime import datetime

import sqlalchemy as sa

from db_infrastructure import metadata, GUID
from store.adapter.store_db import store_product_table, store_product_unit_table, store_supplier_table

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


draft_purchase_order_table = sa.Table(
    'inventory_draft_purchase_order1',
    metadata,
    sa.Column('purchase_order_id', GUID, primary_key=True, default=uuid.uuid4),
    sa.Column('supplier_id', GUID,
              sa.ForeignKey(store_supplier_table.c.supplier_id, onupdate='SET NULL', ondelete='SET NULL')),
    sa.Column('status', sa.String(100), nullable=False, default='new_registration'),
    sa.Column('disabled', sa.Boolean, default='0'),
    sa.Column('version', sa.Integer, nullable=False, default=0),
    sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    sa.Column('last_updated', sa.DateTime, onupdate=datetime.now),
)

draft_purchase_order_items_table = sa.Table(
    'inventory_draft_purchase_order_item',
    metadata,
    sa.Column('purchase_order_id', GUID),
    sa.Column('product_id', GUID),
    sa.Column('unit', sa.String(100), nullable=False),
    sa.Column('quantity', sa.Numeric, default=1, nullable=False),
    sa.Column('description', sa.String(255)),

    sa.ForeignKeyConstraint(('purchase_order_id', 'product_id'),
                            [draft_purchase_order_table.c.purchase_order_id, store_product_table.c.product_id],
                            name='draft_purchase_order_product_fk')
)
inventory_product_balance_table = sa.Table(
    'inventory_balance',
    metadata,
    sa.Column('product_id', GUID),
    sa.Column('unit', sa.String(100)),

    sa.Column('stocking_quantity', sa.Integer, default='0'),

    sa.Column('created_at', sa.DateTime, nullable=False, default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),

    sa.ForeignKeyConstraint(('product_id', 'unit'),
                            [store_product_unit_table.c.product_id, store_product_unit_table.c.unit],
                            name='inventory_balance_product_unit_pk', ondelete='SET NULL')
)
