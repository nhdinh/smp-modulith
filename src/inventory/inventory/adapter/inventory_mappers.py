#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import event
from sqlalchemy.orm import mapper, relationship, backref

from inventory.adapter.inventory_db import draft_purchase_order_table, draft_purchase_order_item_table
from inventory.domain.entities.purchase_order import DraftPurchaseOrder
from inventory.domain.entities.draft_purchase_order_item import DraftPurchaseOrderItem
from inventory.domain.entities.warehouse import Warehouse
from store.adapter.store_db import store_warehouse_table
from store.domain.entities.store import Store
from store.domain.entities.store_address import StoreAddress
from store.domain.entities.store_product import StoreProduct
from store.domain.entities.store_supplier import StoreSupplier
from store.domain.entities.store_unit import StoreProductUnit


def start_mappers():
    mapper(Warehouse, store_warehouse_table, properties={
        '_store': relationship(
            Store,
            viewonly=True
        ),

        '_draft_purchase_orders': relationship(
            DraftPurchaseOrder,
            collection_class=set,
            backref=backref('_warehouse')
        )
    })

    mapper(DraftPurchaseOrder, draft_purchase_order_table, properties={
        '_supplier': relationship(
            StoreSupplier
        ),

        '_delivery_address': relationship(
            StoreAddress
        ),

        '_items': relationship(
            DraftPurchaseOrderItem,
            collection_class=set,
            backref=backref('_purchase_order')
        )
    })

    mapper(DraftPurchaseOrderItem, draft_purchase_order_item_table, properties={
        'product': relationship(
            StoreProduct,
        ),

        'unit': relationship(
            StoreProductUnit
        )
    })


@event.listens_for(Warehouse, 'load')
def warehouse_onload(warehouse, _):
    warehouse._domain_events = []
