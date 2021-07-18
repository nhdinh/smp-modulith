#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlalchemy as sa
import sqlalchemy.orm as orm

from db_infrastructure import metadata
from foundation.value_objects.address import LocationAddress, LocationCountry, LocationCityDivision, \
    LocationCitySubDivision, LocationCity, generate_country_id, generate_city_id, generate_division_id, \
    generate_sub_division_id, generate_address_id

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

location_address_table = sa.Table(
    'location_address',
    metadata,
    sa.Column('address_id', sa.String(40), primary_key=True, default=generate_address_id),
    sa.Column('street_address', sa.String(255)),
    sa.Column('sub_division_id', sa.ForeignKey(location_city_sub_division_table.c.sub_division_id)),
    sa.Column('postal_code', sa.String(100))

)


def start_mappers():
    orm.mapper(LocationCountry, location_country_table, properties={
        'cities': orm.relationship(
            LocationCity,
            backref=orm.backref('_country')
        )
    })

    orm.mapper(LocationCity, location_city_table, properties={
        'divisions': orm.relationship(
            LocationCityDivision,
            backref=orm.backref('_city'),
        ),
    })

    orm.mapper(LocationCityDivision, location_city_division_table, properties={
        'sub_divisions': orm.relationship(
            LocationCitySubDivision,
            backref=orm.backref('_city_division'),
        ),
    })

    orm.mapper(LocationCitySubDivision, location_city_sub_division_table, properties={})

    orm.mapper(LocationAddress, location_address_table, properties={
        'sub_division': orm.relationship(LocationCitySubDivision)
    })
