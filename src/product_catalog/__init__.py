#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector

from product_catalog.catalog_db import collection_table, catalog_table, product_table


__all__ = [
    # database table
    'collection_table', 'catalog_table', 'product_table'
]


class Catalog(injector.Module):
    ...
