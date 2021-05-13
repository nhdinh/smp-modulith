#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlalchemy as sa
from sqlalchemy.orm import mapper, relationship, backref

from auth.domain.entities.role import Role
from auth.domain.entities.user import User
from db_infrastructure import metadata, GUID

user_table = sa.Table(
    'user',
    metadata,
    sa.Column('id', GUID, primary_key=True),
    sa.Column('email', sa.String(255), unique=True),
    sa.Column('password', sa.String(255)),
    sa.Column('active', sa.Boolean),
    sa.Column('confirmed_at', sa.DateTime),
    sa.Column('last_login_at', sa.DateTime),
    sa.Column('current_login_at', sa.DateTime),
    sa.Column('last_login_ip', sa.String(100)),
    sa.Column('current_login_ip', sa.String(100)),
    sa.Column('login_count', sa.Integer)
)

role_table = sa.Table(
    'role',
    metadata,
    sa.Column('id', GUID, primary_key=True),
    sa.Column('name', sa.String(100), unique=True),
    sa.Column('description', sa.String(255))
)

roles_users_table = sa.Table(
    'roles_users',
    metadata,
    sa.Column('user_id', sa.ForeignKey('user.id')),
    sa.Column('role_id', sa.ForeignKey('role.id')),
)


def start_mappers():
    role_mapper = mapper(
        Role,
        role_table
    )

    user_mapper = mapper(
        User,
        user_table,
        properties={
            '_id': user_table.c.id,
            '_roles': relationship(
                role_mapper,
                secondary=roles_users_table,
                collection_class=set,
                backref=backref('users', lazy='dynamic'),
            )
        }
    )
