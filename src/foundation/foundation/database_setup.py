#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlalchemy as sa
import sqlalchemy.orm as orm

from db_infrastructure import metadata
from foundation.value_objects.address import (
    generate_address_id, Address, generate_image_id,
)

"""
location_country_table = sa.Table(
    'location_country',
    metadata,
    sa.Column('country_id', sa.String(40), primary_key=True, default=generate_country_id),
    sa.Column('country_name', sa.String(100), nullable=False, unique=True),
    sa.Column('iso_code', sa.String(100), nullable=False, unique=True)
)

location_city_table = sa.Table(
    'location_city',
    metadata,
    sa.Column('city_id', sa.String(40), primary_key=True, default=generate_city_id),
    sa.Column('country_id', sa.ForeignKey(location_country_table.c.country_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('city_name', sa.String(100), nullable=False, unique=True),

    sa.UniqueConstraint('country_id', 'city_name', name='location_country_city_uix'),
)

location_city_division_table = sa.Table(
    'location_city_division',
    metadata,
    sa.Column('division_id', sa.String(40), primary_key=True, default=generate_division_id),
    sa.Column('city_id', sa.ForeignKey(location_city_table.c.city_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('division_name', sa.String(100), nullable=False),

    sa.UniqueConstraint('city_id', 'division_name', name='location_city_division_uix'),
)

location_city_sub_division_table = sa.Table(
    'location_city_sub_division',
    metadata,
    sa.Column('sub_division_id', sa.String(40), primary_key=True, default=generate_sub_division_id),
    sa.Column('division_id',
              sa.ForeignKey(location_city_division_table.c.division_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('sub_division_name', sa.String(100), nullable=False),

    sa.UniqueConstraint('division_id', 'sub_division_name',
                        name='location_country_city_division_sub_division_uix'),
)

"""

image_info_table = sa.Table(
    'image_info',
    metadata,
    sa.Column('image_id', sa.String(60), primary_key=True, default=generate_image_id)
)

location_address_table = sa.Table(
    'location_address',
    metadata,
    sa.Column('address_id', sa.String(40), primary_key=True, default=generate_address_id),
    sa.Column('street_address', sa.String(255)),
    sa.Column('postal_code', sa.String(100)),
    sa.Column('ward_code', sa.String(20), nullable=False),
    sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
)


def start_mappers():
    orm.mapper(Address, location_address_table)
