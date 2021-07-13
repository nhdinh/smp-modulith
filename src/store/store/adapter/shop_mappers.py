#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy.orm import mapper, relationship, backref

from foundation.value_objects.address import LocationAddress
from store.adapter.shop_db import shop_settings_table, shop_registration_table, shop_user_table, shop_table, \
    shop_users_table, shop_catalog_table, shop_product_table, \
    shop_product_unit_table, shop_brand_table, shop_product_tag_table, shop_collection_table, \
    shop_product_collection_table, shop_warehouse_table, shop_product_supplier_table, shop_supplier_table, \
    shop_supplier_product_price_table, shop_addresses_table, collision_test_table
from store.domain.entities.collision import Collision
from store.domain.entities.purchase_price import ProductPurchasePrice
from store.domain.entities.setting import Setting
from store.domain.entities.shop import Shop
from store.domain.entities.shop_address import ShopAddress
from store.domain.entities.shop_catalog import ShopCatalog
from store.domain.entities.store_collection import ShopCollection
from store.domain.entities.shop_user import ShopUser, SystemUser
from store.domain.entities.store_product import ShopProduct
from store.domain.entities.store_product_brand import ShopProductBrand
from store.domain.entities.store_product_tag import ShopProductTag
from store.domain.entities.shop_registration import ShopRegistration
from store.domain.entities.shop_supplier import ShopSupplier
from store.domain.entities.shop_unit import ShopProductUnit
from store.domain.entities.store_warehouse import Warehouse


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
        SystemUser, shop_user_table, properties={
            'hashed_password': shop_user_table.c.password
        })

    mapper(
        ShopProductUnit, shop_product_unit_table, properties={
            '_referenced_unit': relationship(
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

    mapper(
        ShopProduct, shop_product_table, properties={
            '_shop_id': shop_product_table.c.shop_id,
            '_brand_id': shop_product_table.c.brand_id,
            '_catalog_id': shop_product_table.c.catalog_id,

            '_store': relationship(Shop),

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

    mapper(Warehouse, shop_warehouse_table, properties={})

    mapper(ShopSupplier, shop_supplier_table, properties={})

    mapper(ShopAddress, shop_addresses_table, properties={
        'location_address': relationship(
            LocationAddress
        )
    })

    mapper(ShopUser, shop_users_table, properties={
        'shop_user': relationship(
            SystemUser
        ),
    })

    mapper(
        Shop, shop_table,
        version_id_col=shop_table.c.version,
        version_id_generator=None,
        properties={
            '_settings': relationship(
                Setting,
                collection_class=set,
                backref=backref('_store')
            ),

            '_addresses': relationship(
                ShopAddress,
                collection_class=set,
                backref=backref('_store'),
            ),

            '_warehouses': relationship(
                Warehouse,
                collection_class=set,
            ),

            '_users': relationship(
                ShopUser,
                # secondary=store_managers_table,
                collection_class=set,
            ),

            '_suppliers': relationship(
                ShopSupplier,
                collection_class=set,
            ),

            '_catalogs': relationship(
                ShopCatalog,
                collection_class=set,
                backref=backref('_store')
            ),

            '_collections': relationship(
                ShopCollection,
                collection_class=set,
                backref=backref('_store'),
            ),

            '_products': relationship(
                ShopProduct,
                collection_class=set,
                cascade='all, delete-orphan',
                back_populates='_store',
            ),

            '_brands': relationship(
                ShopProductBrand,
                collection_class=set,
            )
        })

    mapper(
        Collision, collision_test_table
    )
