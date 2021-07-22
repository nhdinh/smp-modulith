#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import event, insert, select
from sqlalchemy.orm import backref, mapper, relationship
from sqlalchemy.sql.functions import count

from foundation.value_objects.address import Address
from shop.adapter.shop_db import (
    shop_addresses_table,
    shop_brand_table,
    shop_catalog_table,
    shop_collection_table,
    shop_product_collection_table,
    shop_product_supplier_table,
    shop_product_table,
    shop_product_tag_table,
    shop_product_unit_table,
    shop_product_view_cache_table,
    shop_registration_table,
    shop_settings_table,
    shop_supplier_product_price_table,
    shop_supplier_table,
    shop_table,
    shop_users_table,
    shop_warehouse_table,
)
from shop.domain.entities.purchase_price import ProductPurchasePrice
from shop.domain.entities.setting import Setting
from shop.domain.entities.shop import Shop
from shop.domain.entities.shop_address import ShopAddress
from shop.domain.entities.shop_catalog import ShopCatalog
from shop.domain.entities.shop_collection import ShopCollection
from shop.domain.entities.shop_product import ShopProduct
from shop.domain.entities.shop_product_brand import ShopProductBrand
from shop.domain.entities.shop_product_cache import ShopProductCache
from shop.domain.entities.shop_product_tag import ShopProductTag
from shop.domain.entities.shop_product_unit import ShopProductUnit
from shop.domain.entities.shop_registration import ShopRegistration
from shop.domain.entities.shop_supplier import ShopSupplier
from shop.domain.entities.shop_user import ShopUser
from shop.domain.entities.shop_warehouse import ShopWarehouse
from shop.domain.entities.value_objects import ShopUserType


def start_mappers():
    mapper(
        Setting, shop_settings_table, properties={
            'key': shop_settings_table.c.setting_key,
            'value': shop_settings_table.c.setting_value,
            'type': shop_settings_table.c.setting_type,
        }
    )

    mapper(
        ShopRegistration, shop_registration_table,
        version_id_col=shop_registration_table.c.version,
        version_id_generator=None,
        properties={
            'registration_id': shop_registration_table.c.shop_registration_id,
            'shop_name': shop_registration_table.c.name,
        }
    )

    mapper(
        ShopProductUnit, shop_product_unit_table, properties={
            'referenced_unit': relationship(
                ShopProductUnit,
                foreign_keys=[shop_product_unit_table.c.product_id, shop_product_unit_table.c.referenced_unit_name],
                remote_side=[shop_product_unit_table.c.product_id, shop_product_unit_table.c.unit_name],
                backref=backref('_inherited_units'),
                overlaps='_inherited_units, product_id'
            ),
        })

    mapper(ShopProductBrand, shop_brand_table)
    mapper(ShopProductTag, shop_product_tag_table)
    mapper(ShopCollection, shop_collection_table)
    mapper(ProductPurchasePrice, shop_supplier_product_price_table,
           properties={
               '_price': shop_supplier_product_price_table.c.price,

               'supplier': relationship(
                   ShopSupplier
               ),

               'product_unit': relationship(
                   ShopProductUnit,
                   overlaps="product, _purchase_prices"
               )
           })

    mapper(ShopProductCache, shop_product_view_cache_table)

    mapper(
        ShopProduct, shop_product_table,
        version_id_col=shop_product_table.c.version,
        version_id_generator=None,
        properties={
            '_shop_id': shop_product_table.c.shop_id,
            '_brand_id': shop_product_table.c.brand_id,
            '_catalog_id': shop_product_table.c.catalog_id,

            '_cache': relationship(ShopProductCache, lazy='select'),

            '_shop': relationship(Shop),

            '_brand': relationship(
                ShopProductBrand
            ),

            '_suppliers': relationship(
                ShopSupplier,
                secondary=shop_product_supplier_table,
                collection_class=set,
                backref=backref('_products'),
            ),

            '_purchase_prices': relationship(
                ProductPurchasePrice,
                collection_class=set,
                # overlaps="_units, product"
            ),

            '_collections': relationship(
                ShopCollection,
                secondary=shop_product_collection_table,
                collection_class=set,
                backref=backref('_products')
            ),

            '_units': relationship(
                ShopProductUnit,
                # backref=backref('_product', cascade='all', single_parent=True),
                collection_class=set,
                overlaps="_inherited_units, product_id"
            ),

            '_tags': relationship(
                ShopProductTag,
                collection_class=set,
            )
        })

    mapper(ShopCatalog, shop_catalog_table,
           properties={
               '_collections': relationship(
                   ShopCollection,
                   collection_class=set,
                   backref=backref('_catalog'),
               ),

               '_products': relationship(
                   ShopProduct,
                   collection_class=set,
                   backref=backref('_catalog'),
               )
           })

    mapper(ShopSupplier, shop_supplier_table, properties={})

    mapper(ShopAddress, shop_addresses_table, properties={
        'address': relationship(
            Address
        )
    })

    mapper(ShopUser, shop_users_table, properties={
        # '_system_user': relationship(
        #     SystemUser
        # ),
    })

    mapper(ShopWarehouse, shop_warehouse_table)

    mapper(
        Shop, shop_table,
        version_id_col=shop_table.c.version,
        version_id_generator=None,
        properties={
            '_settings': relationship(
                Setting,
                collection_class=set,
                backref=backref('_shop')
            ),

            '_addresses': relationship(
                ShopAddress,
                collection_class=set,
                backref=backref('_shop'),
            ),

            '_warehouses': relationship(
                ShopWarehouse,
                collection_class=set,
            ),

            '_users': relationship(
                ShopUser,
                collection_class=set,
            ),

            '_suppliers': relationship(
                ShopSupplier,
                collection_class=set,
            ),

            '_catalogs': relationship(
                ShopCatalog,
                collection_class=set,
                backref=backref('_shop')
            ),

            '_collections': relationship(
                ShopCollection,
                collection_class=set,
                backref=backref('_shop'),
            ),

            '_products': relationship(
                ShopProduct,
                collection_class=set,
                cascade='all, delete-orphan',
                back_populates='_shop',
            ),

            '_brands': relationship(
                ShopProductBrand,
                collection_class=set,
            )
        })


def install_first_data(engine, admin_id: str, admin_email: str, central_db_repo: str, default_repo_cat: str):
    try:
        if engine.execute(select(count(shop_table.c.shop_id))).scalar() == 0:
            first_shop = {
                'shop_id': central_db_repo,
                'name': 'CentralDB',
            }

            first_catalog = {
                'catalog_id': default_repo_cat,
                'shop_id': central_db_repo,
                'title': 'DefaultCatalog',
                'default': True
            }

            engine.execute(insert(shop_table).values(**first_shop))
            engine.execute(insert(shop_catalog_table).values(**first_catalog))
            engine.execute(
                insert(shop_users_table).values(shop_id=central_db_repo, user_id=admin_id, email=admin_email,
                                                shop_role=ShopUserType.ADMIN))
    except Exception as exc:
        raise exc


@event.listens_for(ShopRegistration, 'load')
def shop_registration_load(shop_registration, _):
    shop_registration.domain_events = []


@event.listens_for(ShopProduct, 'load')
def shop_product_load(shop_product, _):
    shop_product.domain_events = []


@event.listens_for(Shop, 'load')
def shop_load(shop, connection):
    shop.domain_events = []

    try:
        shop._admin = next(sm for sm in shop._users if sm.shop_role == ShopUserType.ADMIN)
    except StopIteration:
        shop._admin = None
