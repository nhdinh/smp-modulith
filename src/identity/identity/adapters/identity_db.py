#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlalchemy as sa
from sqlalchemy import event
from sqlalchemy.orm import mapper, relationship, backref

from db_infrastructure import metadata
from identity.adapters.id_generator import generate_user_id, role_id_generator
from identity.domain.entities.revoked_token import RevokedToken
from identity.domain.entities.role import Role
from identity.domain.entities.user import User, UserStatus

user_registration_table = sa.Table(
    'user_registration',
    metadata,
    sa.Column('registration_id', sa.String(40), primary_key=True, default=generate_user_id),
    sa.Column('email', sa.String(255), unique=True, nullable=False),
    sa.Column('password', sa.String(255)),
    sa.Column('mobile_phone', sa.String(255), unique=True),
    sa.Column('confirmation_token', sa.String(200), nullable=False),
    sa.Column('status', sa.String(100), nullable=False, default='new_registration'),
    sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
)

user_table = sa.Table(
    'user',
    metadata,
    sa.Column('user_id', sa.String(40), primary_key=True, default=generate_user_id),
    sa.Column('email', sa.String(255), unique=True),
    sa.Column('mobile', sa.String(255), unique=True),
    sa.Column('password', sa.String(255)),
    sa.Column('status', sa.Enum(UserStatus), nullable=False, default=UserStatus.NORMAL),
    sa.Column('confirmed_at', sa.DateTime),
    sa.Column('last_login_at', sa.DateTime),
    sa.Column('current_login_at', sa.DateTime),
    sa.Column('last_login_ip', sa.String(100)),
    sa.Column('current_login_ip', sa.String(100)),
    sa.Column('login_count', sa.Integer, default=0),
    sa.Column('reset_password_token', sa.String(100)),
    sa.Column('request_reset_password_at', sa.DateTime)
)

role_table = sa.Table(
    'role',
    metadata,
    sa.Column('role_id', sa.String(40), primary_key=True, default=role_id_generator),
    sa.Column('name', sa.String(100), unique=True),
    sa.Column('description', sa.String(255))
)

user_role_table = sa.Table(
    'roles_users',
    metadata,
    sa.Column('user_id', sa.ForeignKey(user_table.c.user_id)),
    sa.Column('role_id', sa.ForeignKey(role_table.c.role_id)),

    sa.UniqueConstraint('user_id', 'role_id', name='user_role_uix'),
    sa.PrimaryKeyConstraint('user_id', 'role_id', name='user_role_pk'),
)

revoked_token_table = sa.Table(
    'revoked_token',
    metadata,
    sa.Column('jti', sa.String(120), unique=True, primary_key=True),
    sa.Column('revoked_on', sa.DateTime)
)


def start_mappers():
    # mapper(
    #     RevokedToken,
    #     revoked_token_table
    # )

    role_mapper = mapper(
        Role,
        role_table
    )

    user_mapper = mapper(
        User,
        user_table,
        properties={
            '_roles': relationship(
                Role,
                secondary=user_role_table,
                primaryjoin=user_table.c.user_id == user_role_table.c.user_id,
                secondaryjoin=role_table.c.role_id == user_role_table.c.role_id,
                collection_class=set,
                backref=backref('_users'),
            )
        }
    )


@event.listens_for(RevokedToken, 'load')
def load_revoked_tokes(token, _):
    # token.revoked_tokens = revoked_token_table.select()
    pass


@event.listens_for(User, 'load')
def user_loaded(user, _):
    user.domain_events = []
