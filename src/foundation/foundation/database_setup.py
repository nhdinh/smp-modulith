#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy import event

from db_infrastructure import metadata, GUID
from foundation.value_objects.location_address import LocationAddress

location_country_table = sa.Table(
    'location_country',
    metadata,
    sa.Column('country_id', GUID, primary_key=True),
    sa.Column('country', sa.String(100), nullable=False, unique=True)
)

location_city_table = sa.Table(
    'location_city',
    metadata,
    sa.Column('city_id', GUID, primary_key=True),
    sa.Column('country', sa.ForeignKey(location_country_table.c.country_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('city', sa.String(100), nullable=False, unique=True),

    sa.UniqueConstraint('country', 'city', name='location_country_city_uix'),
)

location_province_table = sa.Table(
    'location_province',
    metadata,
    sa.Column('province_id', GUID, primary_key=True),
    sa.Column('city', sa.ForeignKey(location_city_table.c.city_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('country', sa.ForeignKey(location_country_table.c.country_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('province', sa.String(100), nullable=False),

    sa.UniqueConstraint('country', 'city', 'province', name='location_country_city_province_uix'),
)

location_address_table = sa.Table(
    'location_address',
    metadata,
    sa.Column('address_id', GUID, primary_key=True),
    sa.Column('street_address', sa.String(255)),
    sa.Column('province', sa.ForeignKey(location_province_table.c.province_id)),
    sa.Column('city', sa.ForeignKey(location_city_table.c.city_id)),
    sa.Column('country', sa.ForeignKey('location_country_table.c.country_id')),
    sa.Column('postal_code', sa.String(100))

)


def start_mappers():
    address_mapper = orm.mapper(LocationAddress, location_address_table, properties={})


@event.listens_for(orm.mapper, 'after_configured')
def location_address_after_configured():
    ...
