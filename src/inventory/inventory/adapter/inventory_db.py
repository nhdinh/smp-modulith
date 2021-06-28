#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlalchemy as sa
from db_infrastructure import metadata, GUID

inventory_product_table = sa.Table(
    'store_product',
    metadata,
    sa.Column('product_id', GUID),
    sa.Column('sku', sa.String(100)),

    extend_existing=True
)
