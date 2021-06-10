#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy

import sqlalchemy as sa

from db_infrastructure import GUID, metadata
from product_catalog.adapter import catalog_db

from store.adapter.store_db import store_table

# store_catalog_table = copy.deepcopy(catalog_db.catalog_table)
store_catalog_table = sa.Table(
    'store_catalog_table',
    metadata,
    sa.Column('catalog_id', GUID, primary_key=True),
    sa.Column('store_id', sa.ForeignKey(store_table.c.store_id)),
    sa.Column('reference', sa.String(100)),
    sa.Column('display_name', sa.String(255), nullable=False),
    sa.Column('system', sa.Boolean, default=False),
    sa.Column('disabled', sa.Boolean, default=False),
    sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),

    # sa.PrimaryKeyConstraint(['store_id', 'reference'], name='store_catalog_pk')
)
