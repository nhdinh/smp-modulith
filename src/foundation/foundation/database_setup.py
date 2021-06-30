#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy import event

from db_infrastructure import metadata, GUID
from foundation.value_objects.address import LocationAddress, LocationCountry, LocationCityDivision, \
    LocationCitySubDivision

location_country_table = sa.Table(
    'location_country',
    metadata,
    sa.Column('country_id', GUID, primary_key=True),
    sa.Column('country_name', sa.String(100), nullable=False, unique=True),
    sa.Column('iso_code', sa.String(100), nullable=False, unique=True)
)

location_city_table = sa.Table(
    'location_city',
    metadata,
    sa.Column('city_id', GUID, primary_key=True),
    sa.Column('country', sa.ForeignKey(location_country_table.c.country_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('city_name', sa.String(100), nullable=False, unique=True),

    sa.UniqueConstraint('country', 'city_name', name='location_country_city_uix'),
)

location_city_division_table = sa.Table(
    'location_city_division',
    metadata,
    sa.Column('division_id', GUID, primary_key=True),
    sa.Column('city', sa.ForeignKey(location_city_table.c.city_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('country', sa.ForeignKey(location_country_table.c.country_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('division_name', sa.String(100), nullable=False),

    sa.UniqueConstraint('country', 'city', 'division_name', name='location_country_city_division_uix'),
)

location_city_sub_division_table = sa.Table(
    'location_city_sub_division',
    metadata,
    sa.Column('sub_division_id', GUID, primary_key=True),
    sa.Column('division',
              sa.ForeignKey(location_city_division_table.c.division_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('city', sa.ForeignKey(location_city_table.c.city_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('country', sa.ForeignKey(location_country_table.c.country_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('sub_division_name', sa.String(100), nullable=False),

    sa.UniqueConstraint('country', 'city', 'division', 'sub_division_name',
                        name='location_country_city_division_sub_division_uix'),
)

location_address_table = sa.Table(
    'location_address',
    metadata,
    sa.Column('address_id', GUID, primary_key=True),
    sa.Column('street_address', sa.String(255)),
    sa.Column('sub_division', sa.ForeignKey(location_city_sub_division_table.c.sub_division_id)),
    sa.Column('division', sa.ForeignKey(location_city_division_table.c.division_id)),
    sa.Column('city', sa.ForeignKey(location_city_table.c.city_id)),
    sa.Column('country', sa.ForeignKey(location_country_table.c.country_id)),
    sa.Column('postal_code', sa.String(100))

)


def start_mappers():
    orm.mapper(LocationCitySubDivision, location_city_sub_division_table, properties={})
    orm.mapper(LocationCityDivision, location_city_division_table, properties={})
    orm.mapper(LocationCountry, location_country_table, properties={})
    orm.mapper(LocationAddress, location_address_table, properties={})
