#!/usr/bin/env python
# -*- coding: utf-8 -*-


from inventory.domain.entities.warehouse import Warehouse
from sqlalchemy.orm import mapper, relationship

from store.adapter.store_db import store_warehouse_table
from store.domain.entities.store import Store


def start_mappers():
    mapper(Warehouse, store_warehouse_table, properties={
        '_store': relationship(
            Store,
            viewonly=True
        )
    })

    pass
