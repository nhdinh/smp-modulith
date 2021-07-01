#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import and_
from sqlalchemy.orm import mapper, relationship, backref, foreign

from identity.domain.entities import User
from store.adapter.store_db import store_settings_table, store_registration_table, store_owner_table, store_table, \
    store_managers_table, store_catalog_table, store_product_table, \
    store_product_unit_table, store_brand_table, store_product_tag_table, store_collection_table, \
    store_product_collection_table, store_warehouse_table, store_product_supplier_table, store_supplier_table, \
    store_supplier_product_price_table, prod_table, ProdClass, sup_table, un_table, SupClass, UnClass, PriClass, \
    sup_un_table, pri_table, prod_sup_table
from store.domain.entities.purchase_price import ProductPurchasePrice
from store.domain.entities.setting import Setting
from store.domain.entities.store import Store
from store.domain.entities.store_catalog import StoreCatalog
from store.domain.entities.store_collection import StoreCollection
from store.domain.entities.store_owner import StoreOwner
from store.domain.entities.store_product import StoreProduct
from store.domain.entities.store_product_brand import StoreProductBrand
from store.domain.entities.store_product_tag import StoreProductTag
from store.domain.entities.store_registration import StoreRegistration
from store.domain.entities.store_supplier import StoreSupplier
from store.domain.entities.store_unit import StoreProductUnit
from store.domain.entities.store_warehouse import StoreWarehouse


def start_mappers():
    mapper(
        Setting, store_settings_table, properties={
            'key': store_settings_table.c.setting_key,
            'value': store_settings_table.c.setting_value,
            'type': store_settings_table.c.setting_type,
        }
    )

    mapper(
        StoreRegistration, store_registration_table,
        version_id_col=store_registration_table.c.version,
        version_id_generator=None,
        properties={
            'registration_id': store_registration_table.c.store_registration_id,
            'store_name': store_registration_table.c.name,
        }
    )

    mapper(
        StoreOwner, store_owner_table, properties={
            'hashed_password': store_owner_table.c.password
        })

    mapper(
        StoreProductUnit, store_product_unit_table, properties={
            # '_product_id': store_product_unit_table.c.product_id,

            'from_unit': relationship(
                StoreProductUnit,
                foreign_keys=[store_product_unit_table.c.product_id, store_product_unit_table.c.base_unit],
                remote_side=[store_product_unit_table.c.product_id, store_product_unit_table.c.unit],
            ),
        })

    mapper(StoreProductBrand, store_brand_table)
    mapper(StoreProductTag, store_product_tag_table)
    mapper(StoreCollection, store_collection_table)
    mapper(ProductPurchasePrice, store_supplier_product_price_table)

    mapper(
        StoreProduct, store_product_table, properties={
            '_store_id': store_product_table.c.store_id,
            '_brand_id': store_product_table.c.brand_id,
            '_catalog_id': store_product_table.c.catalog_id,

            '_store': relationship(Store),

            '_brand': relationship(
                StoreProductBrand
            ),

            '_suppliers': relationship(
                StoreSupplier,
                secondary=store_product_supplier_table,
                collection_class=set,
            ),

            # '_purchase_prices': relationship(
            #     ProductPurchasePrice,
            #     collection_class=set,
            #     primaryjoin=and_(
            #         store_supplier_product_price_table.c.product_id == store_product_table.c.product_id,
            #         store_supplier_product_price_table.c.supplier_id == store_product_supplier_table.c.supplier_id,
            #         store_supplier_product_price_table.c.unit == StoreProductUnit.unit
            #     ),
            # ),

            '_collections': relationship(
                StoreCollection,
                secondary=store_product_collection_table,
                collection_class=set,
            ),

            '_units': relationship(
                StoreProductUnit,
                # backref=backref('_product', cascade='all', single_parent=True),
                collection_class=set,
                # overlaps="_product, product_id",
            ),

            '_tags': relationship(
                StoreProductTag,
                collection_class=set,
            )
        })

    mapper(StoreCatalog, store_catalog_table,
           properties={
               '_collections': relationship(
                   StoreCollection,
                   collection_class=set,
                   backref=backref('_catalog', cascade="all"),
               ),

               '_products': relationship(
                   StoreProduct,
                   collection_class=set,
                   backref=backref('_catalog', cascade='all'),
               )
           })

    mapper(StoreWarehouse, store_warehouse_table, properties={})

    mapper(StoreSupplier, store_supplier_table, properties={})

    mapper(
        Store, store_table,
        version_id_col=store_table.c.version,
        version_id_generator=None,
        properties={
            '_settings': relationship(
                Setting,
                collection_class=set,
                backref=backref('_store')
            ),

            '_store_owner': relationship(
                StoreOwner,
                backref=backref('_store'),
            ),

            '_warehouses': relationship(
                StoreWarehouse,
                collection_class=set,
            ),

            '_managers': relationship(
                User,
                secondary=store_managers_table,
                collection_class=set,
            ),

            '_suppliers': relationship(
                StoreSupplier,
                collection_class=set,
            ),

            '_catalogs': relationship(
                StoreCatalog,
                collection_class=set,
                backref=backref('_store')  # , cascade="all", single_parent=True),
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

    try:
        mapper(SupClass, sup_table)
        mapper(UnClass, un_table)

        mapper(PriClass, pri_table, properties={
            'sup': relationship(
                SupClass,
                secondary=sup_un_table
            ),

            'un': relationship(
                UnClass,
                secondary=sup_un_table
            )
        })
        mapper(ProdClass, prod_table, properties={
            'sups': relationship(
                SupClass,
                collection_class=set,
                secondary=prod_sup_table
            ),

            'uns': relationship(
                UnClass,
                collection_class=set,
            ),

            'pris': relationship(
                PriClass,
                collection_class=set,
                primaryjoin=pri_table.c.prod_id == prod_table.c.id,
                secondary=sup_un_table,
            )
        })
    except Exception as exc:
        raise exc
