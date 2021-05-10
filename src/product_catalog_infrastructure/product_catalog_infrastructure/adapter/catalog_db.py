#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Table, String, Column, Boolean, DateTime, ForeignKey, event
from sqlalchemy.orm import mapper, relationship

from db_infrastructure import metadata, GUID
from product_catalog.domain.entities.catalog import Catalog
from product_catalog.domain.entities.collection import Collection
from product_catalog.domain.entities.product import Product
from product_catalog.domain.entities.tag import Tag

collection_table = Table(
    'collection',
    metadata,
    Column('reference', String(100), primary_key=True),
    Column('display_name', String(255), nullable=False),
    Column('catalog_reference', ForeignKey('catalog.reference')),
    Column('disabled', Boolean, default=0, server_default='0')
)

catalog_table = Table(
    'catalog',
    metadata,
    Column('reference', String(100), primary_key=True),
    Column('display_name', String(255), nullable=False),
    Column('default_collection', ForeignKey(collection_table.c.reference)),
    Column('disabled', Boolean, default=0, server_default='0'),
    Column('created_at', DateTime),
)

product_table = Table(
    'product',
    metadata,
    Column('product_id', GUID, primary_key=True),
    Column('reference', String(100), unique=True, nullable=False),
    Column('display_name', String(255), nullable=False),
    Column('catalog_reference', ForeignKey(catalog_table.c.reference)),
    Column('collection_reference', ForeignKey(collection_table.c.reference))
)

tag_view_table = Table(
    'tag_view',
    metadata,
    Column('tag', String(255), primary_key=True)
)

product_tags_table = Table(
    'product_tag',
    metadata,
    Column('id', ForeignKey(product_table.c.product_id)),
    Column('tag', ForeignKey(tag_view_table.c.tag)),
)


def start_mappers():
    tag_mapper = mapper(
        Tag,
        tag_view_table,
        properties={
            'value': tag_view_table.c.tag
        }
    )

    product_mapper = mapper(
        Product,
        product_table,
        properties={
            '_product_id': product_table.c.product_id,
            '_reference': product_table.c.reference,
            # '_catalog': relationship(
            #     Catalog,
            #     primaryjoin=[catalog_table.c.reference],
            # ),
            '_tags': relationship(
                tag_mapper,
                secondary=product_tags_table,
                collection_class=set
            ),
        }
    )

    collection_mapper = mapper(
        Collection,
        collection_table,
        properties={
            '_products': relationship(
                product_mapper,
                foreign_keys=product_table.c.collection_reference,
                collection_class=set,
                backref='_collection',
            )
        }
    )

    catalog_mapper = mapper(
        Catalog,
        catalog_table,
        properties={
            '_reference': catalog_table.c.reference,
            '_collections': relationship(
                collection_mapper,
                foreign_keys=collection_mapper.c.catalog_reference,
                collection_class=set,
            ),
            '_default_collection': relationship(
                collection_mapper,
                foreign_keys=catalog_table.c.default_collection,
                viewonly=True,
                backref='_catalog'
            )
        }
    )


@event.listens_for(Catalog, "load")
def receive_load(catalog, _):
    catalog._pending_domain_events = []
