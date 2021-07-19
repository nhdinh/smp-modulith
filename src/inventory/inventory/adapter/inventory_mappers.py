#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import event
from sqlalchemy.orm import mapper, relationship, backref

from inventory.adapter.inventory_db import draft_purchase_order_table, draft_purchase_order_item_table, \
    purchase_order_table, purchase_order_item_table, warehouse_table
from inventory.domain.entities.draft_purchase_order import DraftPurchaseOrder
from inventory.domain.entities.draft_purchase_order_item import DraftPurchaseOrderItem
from inventory.domain.entities.purchase_order import PurchaseOrder
from inventory.domain.entities.purchase_order_item import PurchaseOrderItem
from inventory.domain.entities.warehouse import Warehouse
from shop.domain.entities.shop_address import ShopAddress
from shop.domain.entities.shop_supplier import ShopSupplier
from shop.domain.entities.shop_unit import ShopProductUnit
from shop.domain.entities.store_product import ShopProduct


def start_mappers():
    mapper(DraftPurchaseOrderItem, draft_purchase_order_item_table, properties={
        'product': relationship(
            ShopProduct,
            overlaps='unit, product_id'
        ),

        'unit': relationship(
            ShopProductUnit,
            overlaps='product, product_id'
        )
    })

    mapper(DraftPurchaseOrder, draft_purchase_order_table, properties={
        '_supplier': relationship(
            ShopSupplier
        ),

        '_delivery_address': relationship(
            ShopAddress
        ),

        '_items': relationship(
            DraftPurchaseOrderItem,
            collection_class=set,
            backref=backref('_purchase_order')
        ),

        '_approved_purchase_order': relationship(
            PurchaseOrder,
            backref=backref('_draft')
        )
    })

    mapper(PurchaseOrderItem, purchase_order_item_table)

    mapper(PurchaseOrder, purchase_order_table, properties={
        'items': relationship(
            PurchaseOrderItem,
            collection_class=set,
            backref=backref('purchase_order'),
            primaryjoin=purchase_order_table.c.purchase_order_id == purchase_order_item_table.c.purchase_order_id,
        )
    })

    mapper(Warehouse, warehouse_table,
           version_id_col=warehouse_table.c.version,
           version_id_generator=None,
           properties={
               # '_draft_purchase_orders': relationship(
               #     DraftPurchaseOrder,
               #     collection_class=set,
               #     backref=backref('_warehouse')
               # ),
               #
               # '_purchase_orders': relationship(
               #     PurchaseOrder,
               #     collection_class=set,
               #     backref=backref('_warehouse')
               # )
           })


@event.listens_for(Warehouse, 'load')
def warehouse_onload(warehouse, _):
    warehouse._domain_events = []
