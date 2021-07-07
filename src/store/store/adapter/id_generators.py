#!/usr/bin/env python
# -*- coding: utf-8 -*-
from db_infrastructure import nanoid_generate

STORE_ID_PREFIX = 'Store'
WAREHOUSE_ID_PREFIX = 'Warehouse'
STORE_OWNER_ID_PREFIX = 'User'
ADDRESS_ID_PREFIX = 'Address'
STORE_CATALOG_ID_PREFIX = 'Cat'
STORE_COLLECTION_ID_PREFIX = 'Coll'
STORE_SUPPLIER_ID_PREFIX = 'Supplier'
STORE_BRAND_ID_PREFIX = 'Brand'
STORE_PRODUCT_ID_PREFIX = 'Prod'
STORE_PRODUCT_ID_KEYSIZE = (20, 10)
STORE_PRODUCT_PRICE_PREFIX = 'Price'


def generate_store_id():
    return nanoid_generate(prefix=STORE_ID_PREFIX)


def generate_warehouse_id():
    return nanoid_generate(prefix=WAREHOUSE_ID_PREFIX)


def generate_store_owner_id():
    return nanoid_generate(prefix=STORE_OWNER_ID_PREFIX)


def generate_store_address_id():
    return nanoid_generate(prefix=ADDRESS_ID_PREFIX)


def generate_store_catalog_id():
    return nanoid_generate(prefix=STORE_CATALOG_ID_PREFIX)


def generate_store_collection_id():
    return nanoid_generate(prefix=STORE_COLLECTION_ID_PREFIX)


def generate_brand_id():
    return nanoid_generate(prefix=STORE_BRAND_ID_PREFIX)


def generate_supplier_id():
    return nanoid_generate(prefix=STORE_SUPPLIER_ID_PREFIX)


def generate_product_id():
    return nanoid_generate(prefix=STORE_PRODUCT_ID_PREFIX, key_size=STORE_PRODUCT_ID_KEYSIZE)


def generate_product_price_id():
    return nanoid_generate(prefix=STORE_PRODUCT_PRICE_PREFIX)
