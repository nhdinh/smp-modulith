#!/usr/bin/env python
# -*- coding: utf-8 -*-
from db_infrastructure import nanoid_generate

WAREHOUSE_ID_PREFIX = 'Warehouse'
ADDRESS_ID_PREFIX = 'WAddress'
DRAFT_PURCHASE_ORDER_ID_PREFIX = 'DPO'
DRAFT_PURCHASE_ORDER_KEYSIZE = (20, 10)
DRAFT_PURCHASE_ORDER_ITEM_ID_PREFIX = 'DPOI'
PURCHASE_ORDER_ID_PREFIX = 'PO'
PURCHASE_ORDER_KEYSIZE = (20, 10)
DELIVERY_ORDER_ID_PREFIX = 'DO'
DELIVERY_ORDER_KEYSIZE = (20, 10)
DELIVERY_ORDER_ITEM_ID_PREFIX = 'DOI'


def generate_draft_purchase_order_id():
    return nanoid_generate(prefix=DRAFT_PURCHASE_ORDER_ID_PREFIX, key_size=DRAFT_PURCHASE_ORDER_KEYSIZE)


def generate_purchase_order_item_id():
    return nanoid_generate(prefix=DRAFT_PURCHASE_ORDER_ITEM_ID_PREFIX)


def generate_purchase_order_id():
    return nanoid_generate(prefix=PURCHASE_ORDER_ID_PREFIX, key_size=PURCHASE_ORDER_KEYSIZE)


def generate_delivery_order_id():
    return nanoid_generate(prefix=DELIVERY_ORDER_ID_PREFIX, key_size=DELIVERY_ORDER_KEYSIZE)


def generate_delivery_order_item_id():
    return nanoid_generate(prefix=DELIVERY_ORDER_ITEM_ID_PREFIX)


def generate_warehouse_id():
    return nanoid_generate(prefix=WAREHOUSE_ID_PREFIX)


def generate_warehouse_address_id():
    return nanoid_generate(prefix=ADDRESS_ID_PREFIX)
