#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlalchemy as sa

from db_infrastructure import metadata
from store.adapter.store_catalog_db import store_catalog_table
from store.adapter.store_db import store_table

store_catalog_cache_table = sa.Table(
    'store_catalogs_cache',
    metadata,
    sa.Column('store_id', sa.ForeignKey(store_table.c.store_id)),
    sa.Column('catalog_id', sa.ForeignKey(store_catalog_table.c.catalog_id)),
    sa.Column('catalog_reference')
)
