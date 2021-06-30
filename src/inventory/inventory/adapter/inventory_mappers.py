#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy.orm import mapper, relationship

from inventory.adapter.inventory_db import warehouse_table
from inventory.domain.entities.warehouse import Warehouse
from store.domain.entities.store import Store


def start_mappers():
    mapper(Warehouse, warehouse_table, properties={
        '_store': relationship(
            Store,
            backref=None
        )
    })
