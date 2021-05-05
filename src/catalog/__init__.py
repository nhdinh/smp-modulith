#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector

from src import catalog_db

__all__ = [
    'catalog_db'
]


class Catalog(injector.Module):
    ...
