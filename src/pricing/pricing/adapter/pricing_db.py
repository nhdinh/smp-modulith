#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime

import sqlalchemy as sa

from db_infrastructure import metadata
from pricing.adapter.id_generators import generate_purchase_price_id, generate_sell_price_id

pricing_product_table = sa.Table(
    'pricing_products',
    metadata,
    sa.Column('shop_id', sa.String(40)),
    sa.Column('product_id', sa.String(50)),
    sa.Column('title', sa.String(100))
)

pricing_unit_table = sa.Table(
    'pricing_units',
    metadata,
    sa.Column('product_id', sa.String(50)),
    sa.Column('unit_id', sa.String(50)),
    sa.Column('unit_name', sa.String(50))
)

pricing_purchase_price_table = sa.Table(
    'pricing_purchase_price',
    metadata,
    sa.Column('purchase_price_id', sa.String(40), primary_key=True, default=generate_purchase_price_id),
    sa.Column('product_id', sa.String(40), nullable=False),
    sa.Column('supplier_id', sa.String(40), nullable=False),
    sa.Column('unit_id', sa.String(40), nullable=False),

    sa.Column('price', sa.Numeric, nullable=False),
    sa.Column('currency', sa.String(10), nullable=False),
    sa.Column('tax', sa.Numeric, nullable=True),
    sa.Column('effective_from', sa.Date, nullable=False, server_default=sa.func.now()),

    sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, onupdate=datetime.now),

    sa.UniqueConstraint('product_id', 'supplier_id', 'unit_id', 'effective_from', name='purchase_price_uix'),
)

pricing_sell_price_table = sa.Table(
    'pricing_sell_price',
    metadata,
    sa.Column('sell_price_id', sa.String(40), primary_key=True, default=generate_sell_price_id);
)
