#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime

import sqlalchemy as sa

from db_infrastructure import metadata
from inventory.adapter.id_generators import generate_draft_purchase_order_id, generate_purchase_order_id, \
    generate_purchase_order_item_id, generate_delivery_order_id, generate_warehouse_id
from inventory.domain.entities.purchase_order_status import PurchaseOrderStatus
from store.adapter.shop_db import shop_product_table, shop_product_unit_table, shop_supplier_table, \
    shop_addresses_table, shop_warehouse_table

# inventory_product_table = sa.Table(
#     'store_product',
#     metadata,
#     sa.Column('product_id', GUID, primary_key=True),
#     # sa.Column('store_id', sa.ForeignKey(store_table.c.shop_id, ondelete='CASCADE', onupdate='CASCADE')),
#     sa.Column('reference', sa.String(100), nullable=False),
#     sa.Column('title', sa.String(255), nullable=False),
#     sa.Column('sku', sa.String(100), nullable=False),
#     sa.Column('image', sa.String(1000)),
#     # sa.Column('brand_id', sa.ForeignKey(shop_brand_table.c.brand_id), nullable=True),
#     # sa.Column('catalog_id', sa.ForeignKey(shop_catalog_table.c.catalog_id), nullable=True),
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
#     sa.Column('store_id', sa.ForeignKey(store_table.c.shop_id, onupdate='CASCADE', ondelete='CASCADE')),
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

warehouse_table = sa.Table(
    'warehouse',
    metadata,
    sa.Column('warehouse_id', sa.String(40), primary_key=True, default=generate_warehouse_id()),
    sa.Column('admin_id', sa.String(40), nullable=False),
    sa.Column('warehouse_name', sa.String(255), nullable=False),
    sa.Column('default', sa.Boolean, default='0'),
    sa.Column('disabled', sa.Boolean, default='0'),
    sa.Column('version', sa.Integer, nullable=False, default=0),
    sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    sa.Column('last_updated', sa.DateTime, onupdate=datetime.now),
)

purchase_order_table = sa.Table(
    'purchase_order',
    metadata,
    sa.Column('purchase_order_id', sa.String(40), primary_key=True, default=generate_purchase_order_id()),
    sa.Column('warehouse_id',
              sa.ForeignKey(shop_warehouse_table.c.warehouse_id, onupdate='SET NULL', ondelete='SET NULL')),
    sa.Column('approved_date', sa.Date),
    sa.Column('status', sa.Enum(PurchaseOrderStatus), nullable=False, default=PurchaseOrderStatus.APPROVED),
    sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    sa.Column('last_updated', sa.DateTime, onupdate=datetime.now),
)

purchase_order_item_table = sa.Table(
    'purchase_order_item',
    metadata,
    sa.Column('purchase_order_item_id', sa.String(40), primary_key=True, default=generate_purchase_order_item_id),
    sa.Column('purchase_order_id',
              sa.ForeignKey(purchase_order_table.c.purchase_order_id, onupdate='CASCADE', ondelete='CASCADE')),
    sa.Column('product_title', sa.String(255)),
    sa.Column('product_sku', sa.String(50)),
    sa.Column('product_barcode', sa.String(100)),
    sa.Column('brand_title', sa.String(100)),
    sa.Column('brand_logo', sa.String),
    sa.Column('unit', sa.String),
    sa.Column('quantity', sa.Numeric, default=1, nullable=False),
    sa.Column('price_amount', sa.Numeric, nullable=False),
    sa.Column('price_currency', sa.String(10), nullable=False),
    sa.Column('total_amount', sa.Numeric, nullable=False),
    sa.Column('description', sa.String(255))
)

draft_purchase_order_table = sa.Table(
    'draft_purchase_order',
    metadata,
    sa.Column('purchase_order_id', sa.String(40), primary_key=True, default=generate_draft_purchase_order_id),
    sa.Column('warehouse_id',
              sa.ForeignKey(shop_warehouse_table.c.warehouse_id, onupdate='SET NULL', ondelete='SET NULL')),
    sa.Column('supplier_id',
              sa.ForeignKey(shop_supplier_table.c.supplier_id, onupdate='SET NULL', ondelete='SET NULL')),
    sa.Column('shop_address_id',
              sa.ForeignKey(shop_addresses_table.c.shop_address_id, onupdate='SET NULL', ondelete='SET NULL')),
    sa.Column('note', sa.String),
    sa.Column('due_date', sa.Date),
    sa.Column('creator', sa.String(255), nullable=False),
    sa.Column('status', sa.Enum(PurchaseOrderStatus), nullable=False, default=PurchaseOrderStatus.DRAFT),
    sa.Column('approved_id',
              sa.ForeignKey(purchase_order_table.c.purchase_order_id, onupdate='SET NULL', ondelete='SET NULL'),
              nullable=True),
    sa.Column('version', sa.Integer, nullable=False, default=0),
    sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    sa.Column('last_updated', sa.DateTime, onupdate=datetime.now),
)

draft_purchase_order_item_table = sa.Table(
    'draft_purchase_order_item',
    metadata,
    sa.Column('purchase_order_item_id', sa.String(40), primary_key=True, default=generate_purchase_order_item_id),
    sa.Column('purchase_order_id',
              sa.ForeignKey(draft_purchase_order_table.c.purchase_order_id, onupdate='CASCADE', ondelete='CASCADE')),
    sa.Column('product_id', sa.ForeignKey(shop_product_table.c.product_id)),
    sa.Column('unit_unit', sa.String(50), nullable=False),
    sa.Column('quantity', sa.Numeric, default=1, nullable=False),
    sa.Column('description', sa.String(255)),

    sa.UniqueConstraint('purchase_order_id', 'product_id', 'unit_unit', name='draft_purchase_order_product_unit_uix'),
    sa.ForeignKeyConstraint(('product_id', 'unit_unit'),
                            [shop_product_unit_table.c.product_id, shop_product_unit_table.c.unit_name],
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
                            [shop_product_unit_table.c.product_id, shop_product_unit_table.c.unit_name],
                            name='inventory_balance_product_unit_pk', ondelete='SET NULL')
)

delivery_order_table = sa.Table(
    'delivery_order',
    metadata,
    sa.Column('delivery_order_id', sa.String(40), primary_key=True, default=generate_delivery_order_id),
    sa.Column('purchase_order_id', sa.ForeignKey(purchase_order_table.c.purchase_order_id)),
)
