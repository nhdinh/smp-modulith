#!/usr/bin/env python
# -*- coding: utf-8 -*-
from db_infrastructure import nanoid_generate

WAREHOUSE_ID_PREFIX = 'Warehouse'


def generate_draft_purchase_order_id():
    return nanoid_generate(prefix='DPO', key_size=(20, 10))


def generate_purchase_order_item_id():
    return nanoid_generate(prefix='DPOI')


def generate_purchase_order_id():
    return nanoid_generate(prefix='PO', key_size=(20, 10))


def generate_delivery_order_id():
    return nanoid_generate(prefix='DO', key_size=(20, 10))


def generate_delivery_order_item_id():
    return nanoid_generate(prefix='DOI')


def generate_warehouse_id():
    return nanoid_generate(prefix=WAREHOUSE_ID_PREFIX)
