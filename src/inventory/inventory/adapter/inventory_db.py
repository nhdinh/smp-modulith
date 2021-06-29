#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlalchemy as sa
from db_infrastructure import metadata, GUID
from store.adapter import store_table

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

inventory_purchase_order_table = sa.Table(
    'inventory_purchase_order',
    metadata,
    sa.Column('po_id', GUID, primary_key=True),
    sa.Column('store_id', GUID, sa.ForeignKey(store_table.c.store_id)),
    sa.Column('reference', sa.String(100)),
    sa.Column('po_date', sa.DateTime),

    sa.UniqueConstraint('store_id', 'reference', name='inventory_purchase_order_store_reference_uix'),
)

inventory_product_balance_table = sa.Table(
    'inventory_balance',
    metadata,
    sa.Column('product_id', GUID),
    sa.Column('unit', sa.String(100)),

    sa.Column('stocking_quantity', sa.Integer, default='0'),

    sa.Column('created_at', sa.DateTime, nullable=False, default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),

    sa.ForeignKeyConstraint(('product_id', 'unit'), ['store_product_unit.product_id', 'store_product_unit.unit'],
                            name='inventory_balance_productid_unit_pk', ondelete='SET NULL')
)
