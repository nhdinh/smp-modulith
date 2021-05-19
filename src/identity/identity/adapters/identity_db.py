#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlalchemy as sa
from sqlalchemy import event
from sqlalchemy.orm import mapper, relationship, backref

from db_infrastructure import metadata, GUID
from identity.domain.entities.revoked_token import RevokedToken
from identity.domain.entities.role import Role
from identity.domain.entities.user import User

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

revoked_token_table = sa.Table(
    'revoked_token',
    metadata,
    sa.Column('jti', sa.String(120), unique=True, primary_key=True),
    sa.Column('revoked_on', sa.DateTime)
)


def start_mappers():
    mapper(
        RevokedToken,
        revoked_token_table
    )

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


@event.listens_for(RevokedToken, 'load')
def load_revoked_tokes(token, _):
    # token.revoked_tokens = revoked_token_table.select()
    pass
