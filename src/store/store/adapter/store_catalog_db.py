#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy

import sqlalchemy as sa
from product_catalog.adapter import catalog_db

from store.adapter.store_db import store_table

store_catalog_table = copy.deepcopy(catalog_db.catalog_table)
store_catalog_table.name = 'store_catalog_table'
store_catalog_table.append_column(
    sa.Column('store_id', sa.ForeignKey(store_table.c.store_id))
)
