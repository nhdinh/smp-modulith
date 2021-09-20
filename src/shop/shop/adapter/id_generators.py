#!/usr/bin/env python
# -*- coding: utf-8 -*-
from db_infrastructure import nanoid_generate

SHOP_ID_PREFIX = 'Shop'
ADDRESS_ID_PREFIX = 'SAddress'
SHOP_CATALOG_ID_PREFIX = 'Cat'
SHOP_COLLECTION_ID_PREFIX = 'Coll'
SHOP_SUPPLIER_ID_PREFIX = 'Supplier'
SHOP_BRAND_ID_PREFIX = 'Brand'
SHOP_PRODUCT_ID_PREFIX = 'Prod'
SHOP_PRODUCT_ID_KEYSIZE = (20, 10)
SHOP_PRODUCT_PRICE_PREFIX = 'Price'
IMAGE_FILE = 'ShopImg'
PRODUCT_UNIT_ID_PREFIX = 'Unit'
PRODUCT_UNIT_ID_KEYSIZE = (20, 10)


def generate_shop_id():
    return nanoid_generate(prefix=SHOP_ID_PREFIX)


def generate_shop_address_id():
    return nanoid_generate(prefix=ADDRESS_ID_PREFIX)


def generate_shop_catalog_id():
    return nanoid_generate(prefix=SHOP_CATALOG_ID_PREFIX)


def generate_shop_collection_id():
    return nanoid_generate(prefix=SHOP_COLLECTION_ID_PREFIX)


def generate_brand_id():
    return nanoid_generate(prefix=SHOP_BRAND_ID_PREFIX)


def generate_supplier_id():
    return nanoid_generate(prefix=SHOP_SUPPLIER_ID_PREFIX)


def generate_product_id():
    return nanoid_generate(prefix=SHOP_PRODUCT_ID_PREFIX, key_size=SHOP_PRODUCT_ID_KEYSIZE)


def generate_product_unit_id():
    return nanoid_generate(prefix=PRODUCT_UNIT_ID_PREFIX, key_size=PRODUCT_UNIT_ID_KEYSIZE)


def generate_product_purchase_price_id():
    return nanoid_generate(prefix=SHOP_PRODUCT_PRICE_PREFIX)


def generate_image_id():
    return nanoid_generate(prefix=IMAGE_FILE, key_size=(30, 10))
