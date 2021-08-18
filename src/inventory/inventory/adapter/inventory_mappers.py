#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import event
from sqlalchemy.orm import backref, mapper, relationship

from foundation.value_objects.address import Address
from inventory.adapter.inventory_db import (
    purchase_order_item_table,
    purchase_order_table,
    warehouse_addresses_table,
    warehouse_table,
    warehouse_users_table,
)
from inventory.domain.entities.purchase_order import PurchaseOrder
from inventory.domain.entities.purchase_order_item import PurchaseOrderItem
from inventory.domain.entities.value_objects import WarehouseUserType
from inventory.domain.entities.warehouse import Warehouse
from inventory.domain.entities.warehouse_address import WarehouseAddress
from inventory.domain.entities.warehouse_user import WarehouseUser


def start_mappers():
    mapper(WarehouseAddress, warehouse_addresses_table, properties={
        'address': relationship(
            Address
        )
    })

    # mapper(DraftPurchaseOrderItem, draft_purchase_order_item_table, properties={
    #     'product': relationship(
    #         ShopProduct,
    #         overlaps='unit, product_id'
    #     ),
    #
    #     'unit': relationship(
    #         ShopProductUnit,
    #         overlaps='product, product_id'
    #     )
    # })

    # mapper(DraftPurchaseOrder, draft_purchase_order_table, properties={
    #     '_supplier': relationship(
    #         ShopSupplier
    #     ),
    #
    #     '_delivery_address': relationship(
    #         ShopAddress
    #     ),
    #
    #     '_items': relationship(
    #         DraftPurchaseOrderItem,
    #         collection_class=set,
    #         backref=backref('_purchase_order')
    #     ),
    #
    #     '_approved_purchase_order': relationship(
    #         PurchaseOrder,
    #         backref=backref('_draft')
    #     )
    # })

    mapper(PurchaseOrderItem, purchase_order_item_table)

    mapper(PurchaseOrder, purchase_order_table, properties={
        'items': relationship(
            PurchaseOrderItem,
            collection_class=set,
            backref=backref('purchase_order'),
            primaryjoin=purchase_order_table.c.purchase_order_id == purchase_order_item_table.c.purchase_order_id,
        )
    })

    mapper(WarehouseUser, warehouse_users_table, properties={})

    mapper(Warehouse, warehouse_table,
           version_id_col=warehouse_table.c.version,
           version_id_generator=None,
           properties={
               '_users': relationship(
                   WarehouseUser,
                   collection_class=set,
               ),

               '_addresses': relationship(
                   WarehouseAddress,
                   collection_class=set,
                   backref=backref('_store'),
               ),

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
    warehouse.domain_events = []

    try:
        warehouse._admin = next(wm for wm in warehouse._users if wm.warehouse_role == WarehouseUserType.ADMIN)
    except StopIteration:
        warehouse._admin = None

#
# @event.listens_for(DraftPurchaseOrder, 'load')
# def dpo_onload(dpo, _):
#     dpo.domain_events = []
