#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlalchemy as sa
from sqlalchemy import and_
from sqlalchemy.orm import mapper, relationship, foreign

from db_infrastructure import metadata
from pricing.adapter.id_generators import generate_price_id
from pricing.domain.priced_item import PricedItem
from pricing.domain.value_objects import ResourceOwner, PurchasePrice, SellPrice, PriceTypes, Price

pricing_user_table = sa.Table(
    'pricing_users',
    metadata,
    sa.Column('user_id', sa.String(40), primary_key=True),
    sa.Column('email', sa.String(255), unique=True),
    sa.Column('status', sa.String(30)),
    sa.Column('created_at', sa.DateTime, nullable=False, default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
)

pricing_priced_items_table = sa.Table(
    'pricing_priced_items',
    metadata,
    sa.Column('product_id', sa.String(40), primary_key=True),
    sa.Column('owner_id', sa.String(40)),
    sa.Column('shop_id', sa.String(40)),
    sa.Column('sku', sa.String(100), nullable=False),
    sa.Column('title', sa.String(255), nullable=False),
    sa.Column('status', sa.String(40)),
    sa.Column('version', sa.Integer, default=0),
    sa.Column('created_at', sa.DateTime, nullable=False, default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
)

pricing_price_table = sa.Table(
    'pricing_price',
    metadata,
    sa.Column('price_id', sa.String(40), primary_key=True, default=generate_price_id),
    sa.Column('product_id', sa.String(40), nullable=False),
    sa.Column('unit_id', sa.String(40), nullable=False),
    sa.Column('unit_name', sa.String(50), nullable=False),
    sa.Column('price_type', sa.Enum(PriceTypes), nullable=False),

    sa.Column('price', sa.Numeric, nullable=False),
    sa.Column('currency', sa.String(10), nullable=False),
    sa.Column('tax', sa.Numeric, nullable=True),
    sa.Column('effective_from', sa.Date, nullable=False, server_default=sa.func.now()),
    sa.Column('expired_on', sa.Date, nullable=True),

    sa.Column('created_at', sa.DateTime, nullable=False, default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()), )


def pricing_mapper():
    mapper(
        ResourceOwner, pricing_user_table
    )

    mapper(
        Price, pricing_price_table
    )

    mapper(
        PricedItem, pricing_priced_items_table,
        properties={
            '_owner': relationship(
                ResourceOwner,
                primaryjoin=pricing_user_table.c.user_id == foreign(pricing_priced_items_table.c.owner_id)
            ),

            'purchase_prices': relationship(
                Price,
                primaryjoin=and_(foreign(pricing_price_table.c.product_id) == pricing_priced_items_table.c.product_id,
                                 pricing_price_table.c.price_types == PriceTypes.PURCHASE),
                back_populates='_product',
                collection_class=set,
            ),

            'sell_price': relationship(
                Price,
                primaryjoin=and_(foreign(pricing_price_table.c.product_id) == pricing_priced_items_table.c.product_id,
                                 pricing_price_table.c.price_types == PriceTypes.SELL),
                back_populates='_product',
                collection_class=set,
            )
        }
    )
