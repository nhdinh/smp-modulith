#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Table, String, Column, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import mapper, relationship

from db_infrastructure import metadata, GUID
from product_catalog.domain.entities.catalog import Catalog
from product_catalog.domain.entities.collection import Collection

collection_table = Table(
    'collection',
    metadata,
    Column('reference', String(100), primary_key=True),
    Column('display_name', String(255), nullable=False),
    Column('catalog_id', ForeignKey('catalog.id')),
    Column('disabled', Boolean, default=0, server_default='0')
)

catalog_table = Table(
    'catalog',
    metadata,
    Column('id', GUID, primary_key=True),
    Column('reference', String(100), unique=True, nullable=False),
    Column('display_name', String(255), nullable=False),
    Column('default_collection', ForeignKey(collection_table.c.reference)),
    Column('disabled', Boolean, default=0, server_default='0'),
    Column('created_at', DateTime),
)

product_table = Table(
    'product',
    metadata,
    Column('id', GUID, primary_key=True)
)


def start_mappers():
    collection_mapper = mapper(
        Collection,
        collection_table
    )

    catalog_mapper = mapper(
        Catalog,
        catalog_table
    )
