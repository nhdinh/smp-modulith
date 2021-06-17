#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy.orm import mapper, relationship, backref

from identity.domain.entities import User
from store.adapter.store_db import store_settings_table, store_registration_table, store_owner_table, store_table, \
    store_managers_table, store_catalog_table, store_collection_table, store_brand_table, store_product_table, \
    store_product_brands_table, store_product_unit_table
from store.domain.entities.setting import Setting
from store.domain.entities.store import Store
from store.domain.entities.store_catalog import StoreCatalog
from store.domain.entities.store_collection import StoreCollection
from store.domain.entities.store_owner import StoreOwner
from store.domain.entities.store_product import StoreProduct
from store.domain.entities.store_product_brand import StoreProductBrand
from store.domain.entities.store_registration import StoreRegistration
from store.domain.entities.store_unit import StoreProductUnit


def start_mappers():
    mapper(
        Setting,
        store_settings_table,
        properties={
            'key': store_settings_table.c.setting_key,
            'value': store_settings_table.c.setting_value,
            'type': store_settings_table.c.setting_type,
        }
    )

    mapper(
        StoreRegistration,
        store_registration_table,
        properties={
            'registration_id': store_registration_table.c.store_registration_id,
            'store_name': store_registration_table.c.name,
        }
    )

    owner = mapper(
        StoreOwner,
        store_owner_table,
        properties={
            'hashed_password': store_owner_table.c.password
        }
    )

    mapper(
        StoreProductUnit,
        store_product_unit_table,
        properties={
            '_product_id': store_product_unit_table.c.product_id,
            '_base_product_id': store_product_unit_table.c.base_product_id,
            'from_unit': relationship(
                StoreProductUnit,
                foreign_keys=[store_product_unit_table.c.base_product_id, store_product_unit_table.c.base_unit],
                remote_side=[store_product_unit_table.c.product_id, store_product_unit_table.c.unit],
            ),
        })

    mapper(StoreProductBrand, store_brand_table)

    mapper(
        StoreProduct, store_product_table,
        properties={
            '_brand': relationship(
                StoreProductBrand,
                secondary=store_product_brands_table
            ),

            '_units': relationship(
                StoreProductUnit,
                collection_class=set
            )
        })

    mapper(
        StoreCollection, store_collection_table,
        properties={
            '_store_id': store_collection_table.c.store_id,

            '_products': relationship(
                StoreProduct,
                collection_class=set,
                cascade='all, delete-orphan',
                backref=backref('_collection', cascade='all', single_parent=True)
            ),
        })

    mapper(StoreCatalog, store_catalog_table, properties={
        '_collections': relationship(
            StoreCollection,
            collection_class=set,
            cascade='all, delete-orphan',
            backref=backref('_catalog', cascade="all", single_parent=True),
        )
    })

    store_mapper = mapper(
        Store, store_table,
        version_id_col=store_table.c.version,
        version_id_generator=None,
        properties={
            '_owner_id': store_table.c.owner,
            'owner_email': store_table.c.owner_email,

            '_settings': relationship(
                Setting,
                collection_class=set
            ),

            '_owner': relationship(
                StoreOwner,
                # foreign_keys=[store_table.c.owner],
                # remote_side=[store_owner_table.c.id],
                # viewonly=True,
                backref=backref('_store'),
            ),

            '_managers': relationship(
                User,
                secondary=store_managers_table,
                collection_class=set,
            ),

            '_catalogs': relationship(
                StoreCatalog,
                collection_class=set,
                cascade='all, delete-orphan',
                backref=backref('_store', cascade="all", single_parent=True),
                # single_parent=True
            ),

            '_collections': relationship(
                StoreCollection,
                collection_class=set,
                backref=backref('_store'),
                # viewonly=True,
            ),

            '_brands': relationship(
                StoreProductBrand,
                collection_class=set,
                backref=backref('_store', cascade='all', single_parent=True),
            )
        })
