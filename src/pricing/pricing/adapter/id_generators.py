#!/usr/bin/env python
# -*- coding: utf-8 -*-
from db_infrastructure import nanoid_generate

PURCHASE_PRICE_PREFIX = 'PPrice'
SELL_PRICE_PREFIX = 'SPrice'


def generate_purchase_price_id():
    return nanoid_generate(prefix=PURCHASE_PRICE_PREFIX)


def generate_sell_price_id():
    return nanoid_generate(prefix=SELL_PRICE_PREFIX)
