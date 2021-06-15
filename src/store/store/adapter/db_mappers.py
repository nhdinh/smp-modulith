#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy.orm import mapper, relationship, backref

from identity.domain.entities import User
from store.adapter.store_db import store_settings_table, store_registration_table, store_owner_table, store_table, \
    store_managers_table, store_catalog_table, store_collection_table
from store.domain.entities.setting import Setting
from store.domain.entities.store import Store
from store.domain.entities.store_catalog import StoreCatalog
from store.domain.entities.store_collection import StoreCollection
from store.domain.entities.store_owner import StoreOwner
from store.domain.entities.store_registration import StoreRegistration


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

    mapper(StoreCollection, store_collection_table, properties={
        '_store_id': store_collection_table.c.store_id,
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
            )
        })
