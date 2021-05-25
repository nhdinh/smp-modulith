#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import Table, String, Column, Boolean, DateTime, ForeignKey, event, func, Float, Numeric, \
    PrimaryKeyConstraint, ForeignKeyConstraint
from sqlalchemy.orm import mapper, relationship, backref

from db_infrastructure import metadata, GUID
from product_catalog.domain.entities.brand import Brand
from product_catalog.domain.entities.catalog import Catalog
from product_catalog.domain.entities.collection import Collection
from product_catalog.domain.entities.product import Product
from product_catalog.domain.entities.product_unit import ProductUnit
from product_catalog.domain.entities.tag import Tag
from product_catalog.domain.entities.unit import Unit

collection_table = Table(
    'collection',
    metadata,
    Column('reference', String(100), unique=True, nullable=False, primary_key=True),
    Column('display_name', String(255), nullable=False),
    Column('catalog_reference', ForeignKey('catalog.reference'), nullable=False, primary_key=True),
    Column('disabled', Boolean, default=0, server_default='0'),
    Column('default', Boolean, default=0, server_default='0'),
    Column('created_at', DateTime, server_default=func.now()),
    Column('last_updated', DateTime, onupdate=datetime.now),
)

catalog_table = Table(
    'catalog',
    metadata,
    Column('reference', String(100), primary_key=True),
    Column('display_name', String(255), nullable=False),
    Column('disabled', Boolean, default=0, server_default='0'),
    Column('created_at', DateTime, server_default=func.now()),
    Column('last_updated', DateTime, default=datetime.now),
)

brand_table = Table(
    'brand',
    metadata,
    Column('reference', String(100), primary_key=True),
    Column('display_name', String(255), nullable=False),
    Column('disabled', Boolean, default=0, server_default='0'),
    Column('created_at', DateTime, server_default=func.now()),
    Column('last_updated', DateTime, onupdate=datetime.now),
)

seller_table = Table(
    'seller',
    metadata,
    Column('phone_number', String(255), primary_key=True),
    Column('full_name', String(255)),
    Column('disabled', Boolean, default=0, server_default='0'),
    Column('created_at', DateTime, server_default=func.now()),
    Column('last_updated', DateTime, onupdate=datetime.now),

)

product_table = Table(
    'product',
    metadata,
    Column('product_id', GUID, primary_key=True),
    Column('reference', String(100), unique=True, nullable=False),
    Column('display_name', String(255), nullable=False),
    Column('catalog_reference', ForeignKey(catalog_table.c.reference, ondelete='SET NULL')),
    Column('collection_reference', ForeignKey(collection_table.c.reference, ondelete='SET NULL')),
    Column('brand_reference', ForeignKey(brand_table.c.reference, ondelete='SET NULL')),
    Column('created_at', DateTime, server_default=func.now()),
    Column('last_updated', DateTime, onupdate=datetime.now),
)

tag_view_table = Table(
    'tag_view',
    metadata,
    Column('tag', String(255), primary_key=True)
)

unit_table = Table(
    'unit',
    metadata,
    Column('title', String(50), unique=True, primary_key=True)
)

product_unit_table = Table(
    'product_unit',
    metadata,

    Column('product_id', GUID, ForeignKey(product_table.c.product_id)),
    Column('unit', String(50)),

    Column('default', Boolean, server_default='0'),

    Column('multiplier', Numeric, nullable=True, server_default='1'),

    Column('base_product_id', nullable=True, default=None),
    Column('base_unit', nullable=True, default=None),

    Column('disabled', Boolean, default=False, server_default='0'),
    Column('created_at', DateTime, nullable=False, server_default=func.now()),
    Column('last_updated', DateTime, nullable=False, onupdate=datetime.now),

    PrimaryKeyConstraint('product_id', 'unit', name='product_unit_pk'),
    ForeignKeyConstraint(
        ('base_product_id', 'base_unit'),
        ['product_unit.product_id', 'product_unit.unit'],
        name='product_unit_fk',
        onupdate='SET NULL',
        ondelete='SET NULL'
    )
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

    brand_mapper = mapper(
        Brand,
        brand_table,
        properties={
            '_products': relationship(
                Product,
                collection_class=set,
                backref=backref('_brand'),
            )
        }
    )

    mapper(
        Unit,
        unit_table,
    )

    product_unit_mapper = mapper(
        ProductUnit,
        product_unit_table,
        properties={
            '_product_id': product_unit_table.c.product_id,
            '_unit': product_unit_table.c.unit,
            '_base_product_id': product_unit_table.c.base_product_id,
            '_base_unit': product_unit_table.c.base_unit,

            # '_product': relationship(
            #     Product,
            #     foreign_keys=[product_unit_table.c.product_id],
            #     backref=backref('_units'),
            #     viewonly=True,
            # ),

            '_base': relationship(
                ProductUnit,
                foreign_keys=[product_unit_table.c.base_product_id, product_unit_table.c.base_unit],
                remote_side=[product_unit_table.c.product_id, product_unit_table.c.unit],
            ),
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
                Tag,
                secondary=product_tags_table,
                collection_class=set
            ),
            '_units': relationship(
                ProductUnit,
                backref=backref('_product', remote_side=[product_unit_table.c.product_id]),
                collection_class=set,
            )
        }
    )

    collection_mapper = mapper(
        Collection,
        collection_table,
        properties={
            '_products': relationship(
                Product,
                foreign_keys=product_table.c.collection_reference,
                collection_class=set,
                backref='_collection',
            ),
        }
    )

    catalog_mapper = mapper(
        Catalog,
        catalog_table,
        properties={
            '_reference': catalog_table.c.reference,
            '_collections': relationship(
                Collection,
                backref=backref('_catalog', remote_side=[catalog_table.c.reference]),
                collection_class=set,
            )
        }
    )


@event.listens_for(Catalog, "load")
def receive_load(catalog, _):
    catalog._pending_domain_events = []

    # set default_collection for the catalog
    if not hasattr(catalog, '_default_collection') or not getattr(catalog, '_default_collection', None):
        if len(catalog.collections) == 0:
            default_collection = None
        elif len(catalog.collections) == 1:
            default_collection = next(iter(catalog.collections))
            default_collection.default = True
        else:
            try:
                default_collection = next(c for c in catalog.collections if c.default)
            except StopIteration:
                default_collection = next(iter(catalog.collections))
                default_collection.default = True

        setattr(catalog, '_default_collection', default_collection)
