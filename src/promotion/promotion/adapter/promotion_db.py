#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlalchemy as sa

from db_infrastructure import metadata

promo_product_table = sa.Table(
    'promo_product',
    metadata,
    sa.Column('shop_id'),
    sa.Column('product_title')
)
