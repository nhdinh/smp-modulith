#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlalchemy as sa

from db_infrastructure import metadata
from recommendation.domain.value_objects import RecommendationTypes

from recommendation.adapter.id_generators import generate_recommend_group_id

rec_product_list_table = sa.Table(
    'r_products',
    metadata,
    sa.Column('shop_id', sa.String(40), nullable=False),
    sa.Column('product_id', sa.String(40), nullable=False),
    sa.Column('title', sa.String(100), nullable=False),
    sa.Column('sku', sa.String(100), nullable=False),

    sa.PrimaryKeyConstraint('shop_id', 'product_id'),
)

rec_recommendation_group_table = sa.Table(
    'r_recommendation_group',
    metadata,
    sa.Column('shop_id', sa.String(40), nullable=False),
    sa.Column('group_id', sa.String(40), primary_key=True, default=generate_recommend_group_id),
    sa.Column('name', sa.String(100), nullable=False),
    sa.Column('rec_type', sa.Enum(RecommendationTypes)),
    sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now())
)

rec_recommendation_details_table = sa.Table(
    'r_recommendation_details',
    metadata,
    sa.Column('shop_id'),
    sa.Column('group_id'),
    sa.Column('product_id')
)