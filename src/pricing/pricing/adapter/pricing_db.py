#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlalchemy as sa
from sqlalchemy import and_
from sqlalchemy.orm import mapper, relationship, foreign

from db_infrastructure import metadata
from pricing.adapter.id_generators import generate_price_id
from pricing.domain.priced_item import PricedItem
from pricing.domain.value_objects import ResourceOwner, PriceTypes, Price, GenericItemStatus, PriceStatus, \
    MeasurementUnit

pricing_user_table = sa.Table(
    'pricing_users',
    metadata,
    sa.Column('user_id', sa.String(40), nullable=False, primary_key=True),
    sa.Column('email', sa.String(255)),
    sa.Column('status', sa.Enum(GenericItemStatus)),
    sa.Column('created_at', sa.DateTime, nullable=False, default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
)

pricing_unit_table = sa.Table(
    'pricing_units',
    metadata,
    sa.Column('unit_id', sa.String(40), nullable=False),
    sa.Column('product_id', sa.String(40), nullable=False),
    sa.Column('unit_name', sa.String(50)),
)

pricing_priced_items_table = sa.Table(
    'pricing_priced_items',
    metadata,
    sa.Column('product_id', sa.String(40), nullable=False),
    sa.Column('owner_id', sa.String(40), nullable=False),
    sa.Column('shop_id', sa.String(40), nullable=False),
    sa.Column('sku', sa.String(100)),
    sa.Column('title', sa.String(255)),
    sa.Column('status', sa.Enum(GenericItemStatus)),
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

    sa.Column('price_type', sa.Enum(PriceTypes), nullable=False),

    sa.Column('price', sa.Numeric, nullable=False),
    sa.Column('currency', sa.String(10), nullable=False),
    sa.Column('tax', sa.Numeric, nullable=True),

    sa.Column('status', sa.Enum(PriceStatus), nullable=False, default=PriceStatus.NORMAL),
    sa.Column('effective_from', sa.Date, nullable=False, server_default=sa.func.now()),
    sa.Column('expired_on', sa.Date, nullable=True),

    sa.Column('created_at', sa.DateTime, nullable=False, default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()), )


def pricing_mapper():
    mapper(
        ResourceOwner, pricing_user_table
    )

    mapper(
        MeasurementUnit, pricing_unit_table,
    )

    mapper(
        Price, pricing_price_table,
        properties={
            '_price_id': pricing_price_table.c.price_id
        }
    )

    mapper(
        PricedItem, pricing_priced_items_table,
        properties={
            '_owner': relationship(
                ResourceOwner,
                primaryjoin=pricing_user_table.c.user_id == foreign(pricing_priced_items_table.c.owner_id)
            ),

            'units': relationship(
                MeasurementUnit,
                primaryjoin=pricing_price_table.c.product_id == foreign(pricing_unit_table.c.product_id),
            ),

            'purchase_prices': relationship(
                Price,
                primaryjoin=and_(foreign(pricing_price_table.c.product_id) == pricing_priced_items_table.c.product_id,
                                 pricing_price_table.c.price_type == PriceTypes.PURCHASE),
                overlaps="sell_prices, product_id",
                collection_class=set,
            ),

            'sell_prices': relationship(
                Price,
                primaryjoin=and_(foreign(pricing_price_table.c.product_id) == pricing_priced_items_table.c.product_id,
                                 pricing_price_table.c.price_type == PriceTypes.SELL),
                overlaps="purchase_prices, product_id",
                collection_class=set,
            )
        }
    )
