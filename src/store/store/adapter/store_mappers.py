#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy.orm import mapper, relationship, backref

from foundation.value_objects.address import LocationAddress
from store.adapter.store_db import shop_settings_table, shop_registration_table, shop_user_table, shop_table, \
    shop_managers_table, shop_catalog_table, shop_product_table, \
    store_product_unit_table, store_brand_table, store_product_tag_table, shop_collection_table, \
    shop_product_collection_table, shop_warehouse_table, store_product_supplier_table, store_supplier_table, \
    store_supplier_product_price_table, shop_addresses_table, collision_test_table
from store.domain.entities.collision import Collision
from store.domain.entities.purchase_price import ProductPurchasePrice
from store.domain.entities.setting import Setting
from store.domain.entities.shop import Shop
from store.domain.entities.shop_address import ShopAddress
from store.domain.entities.store_catalog import StoreCatalog
from store.domain.entities.store_collection import StoreCollection
from store.domain.entities.shop_manager import ShopManager
from store.domain.entities.shop_user import ShopUser
from store.domain.entities.store_product import StoreProduct
from store.domain.entities.store_product_brand import StoreProductBrand
from store.domain.entities.store_product_tag import StoreProductTag
from store.domain.entities.shop_registration import ShopRegistration
from store.domain.entities.store_supplier import StoreSupplier
from store.domain.entities.store_unit import StoreProductUnit
from store.domain.entities.store_warehouse import StoreWarehouse


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
        ShopUser, shop_user_table, properties={
            'hashed_password': shop_user_table.c.password
        })

    mapper(
        StoreProductUnit, store_product_unit_table, properties={
            '_referenced_unit': relationship(
                StoreProductUnit,
                foreign_keys=[store_product_unit_table.c.product_id, store_product_unit_table.c.referenced_unit_name],
                remote_side=[store_product_unit_table.c.product_id, store_product_unit_table.c.unit_name],
                backref=backref('_inherited_units'),
                overlaps='_inherited_units, product_id'
            ),
        })

    mapper(StoreProductBrand, store_brand_table)
    mapper(StoreProductTag, store_product_tag_table)
    mapper(StoreCollection, shop_collection_table)
    mapper(ProductPurchasePrice, store_supplier_product_price_table,
           properties={
               '_price': store_supplier_product_price_table.c.price,

               'supplier': relationship(
                   StoreSupplier
               ),

               'product_unit': relationship(
                   StoreProductUnit,
                   overlaps="product, _purchase_prices"
               )
           })

    mapper(
        StoreProduct, shop_product_table, properties={
            '_store_id': shop_product_table.c.shop_id,
            '_brand_id': shop_product_table.c.brand_id,
            '_catalog_id': shop_product_table.c.catalog_id,

            '_store': relationship(Shop),

            '_brand': relationship(
                StoreProductBrand
            ),

            '_suppliers': relationship(
                StoreSupplier,
                secondary=store_product_supplier_table,
                collection_class=set,
                backref=backref('_products'),
            ),

            '_purchase_prices': relationship(
                ProductPurchasePrice,
                collection_class=set,
                # overlaps="_units, product"
            ),

            '_collections': relationship(
                StoreCollection,
                secondary=shop_product_collection_table,
                collection_class=set,
                backref=backref('_products')
            ),

            '_units': relationship(
                StoreProductUnit,
                # backref=backref('_product', cascade='all', single_parent=True),
                collection_class=set,
                overlaps="_inherited_units, product_id"
            ),

            '_tags': relationship(
                StoreProductTag,
                collection_class=set,
            )
        })

    mapper(StoreCatalog, shop_catalog_table,
           properties={
               '_collections': relationship(
                   StoreCollection,
                   collection_class=set,
                   backref=backref('_catalog'),
               ),

               '_products': relationship(
                   StoreProduct,
                   collection_class=set,
                   backref=backref('_catalog'),
               )
           })

    mapper(StoreWarehouse, shop_warehouse_table, properties={})

    mapper(StoreSupplier, store_supplier_table, properties={})

    mapper(ShopAddress, shop_addresses_table, properties={
        'location_address': relationship(
            LocationAddress
        )
    })

    mapper(ShopManager, shop_managers_table, properties={
        'shop_user': relationship(
            ShopUser
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
                StoreWarehouse,
                collection_class=set,
            ),

            '_managers': relationship(
                ShopManager,
                # secondary=store_managers_table,
                collection_class=set,
            ),

            '_suppliers': relationship(
                StoreSupplier,
                collection_class=set,
            ),

            '_catalogs': relationship(
                StoreCatalog,
                collection_class=set,
                backref=backref('_store')
            ),

            '_collections': relationship(
                StoreCollection,
                collection_class=set,
                backref=backref('_store'),
            ),

            '_products': relationship(
                StoreProduct,
                collection_class=set,
                cascade='all, delete-orphan',
                back_populates='_store',
            ),

            '_brands': relationship(
                StoreProductBrand,
                collection_class=set,
            )
        })

    mapper(
        Collision, collision_test_table
    )
