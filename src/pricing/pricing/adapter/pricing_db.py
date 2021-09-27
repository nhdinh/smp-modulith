#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlalchemy as sa
from sqlalchemy.orm import mapper

from db_infrastructure import metadata

pricing_user_table = sa.Table(
    'pricing_users',
    metadata,
    sa.Column('user_id'),
    sa.Column('username'),
    sa.Column('status'),
)

pricing_priced_items_table = sa.Table(
    'pricing_priced_items',
    metadata,
    sa.Column('product_id'),
    sa.Column('owner_id'),
    sa.Column('shop_id'),
    sa.Column('title'),
    sa.Column('version', sa.Integer),
    sa.Column('created_at'),
    sa.Column('updated_at')
)

pricing_purchase_price_table = sa.Table(
    'pricing_purchase_price',
    metadata,
    sa.Column('purchase_price_id'),
    sa.Column('product_id'),

)

pricing_sell_price_table = sa.Table()

# mapper(
#     ProductPurchasePrice, shop_product_purchase_price_table,
#     properties={
#         '_price': shop_product_purchase_price_table.c.price,
#
#         'supplier': relationship(
#             ShopSupplier,
#             primaryjoin=shop_supplier_table.c.supplier_id == foreign(
#                 shop_product_purchase_price_table.c.supplier_id),
#         ),
#
#         'product_unit': relationship(
#             ShopProductUnit,
#             primaryjoin=shop_product_unit_table.c.unit_id == foreign(shop_product_purchase_price_table.c.unit_id)
#         ),
#
#         '_product': relationship(
#             ShopProduct,
#             primaryjoin=shop_product_table.c.product_id == foreign(shop_product_purchase_price_table.c.product_id),
#             back_populates='_purchase_prices'
#         )
#     }
# )
