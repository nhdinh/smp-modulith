#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import event, insert, select
from sqlalchemy.orm import backref, mapper, relationship
from sqlalchemy.sql.functions import count

from db_infrastructure import metadata
from identity.adapters.id_generator import generate_user_id, role_id_generator
from identity.domain.entities.revoked_token import RevokedToken
from identity.domain.entities.role import Role, SystemRoleEnum
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
    sa.Column('failed_login_count', sa.Integer),
    sa.Column('reset_password_token', sa.String(100)),
    sa.Column('request_reset_password_at', sa.DateTime),
    sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, onupdate=datetime.now),
)

role_table = sa.Table(
    'role',
    metadata,
    sa.Column('role_id', sa.String(40), primary_key=True, default=role_id_generator),
    sa.Column('name', sa.Enum(SystemRoleEnum), nullable=False, unique=True, default=SystemRoleEnum.SystemUser),
    sa.Column('description', sa.String(255))
)

user_role_table = sa.Table(
    'roles_users',
    metadata,
    sa.Column('user_id', sa.ForeignKey(user_table.c.user_id, ondelete='CASCADE', onupdate='CASCADE')),
    sa.Column('role_id', sa.ForeignKey(role_table.c.role_id, ondelete='CASCADE', onupdate='CASCADE')),

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


def install_first_data(engine, admin_id: str, sysadmin_role_id: str, sysuser_role_id: str, admin_email: str,
                       admin_password: str):
    try:
        if engine.execute(select(count(user_table.c.user_id))).scalar() == 0:
            sysadmin_role = {
                'role_id': sysadmin_role_id,
                'name': 'SystemAdmin',
                'description': 'SystemAdmin Role'
            }

            sysuser_role = {
                'role_id': sysuser_role_id,
                'name': 'SystemUser',
                'description': 'SystemUser Role'
            }

            first_user = {
                'user_id': admin_id,
                'email': admin_email,
                'mobile': '',
                'password': User.generate_hash(admin_password)
            }

            engine.execute(insert(role_table).values(**sysadmin_role))
            engine.execute(insert(role_table).values(**sysuser_role))
            engine.execute(insert(user_table).values(**first_user))
            engine.execute(insert(user_role_table).values(user_id=admin_id, role_id=sysadmin_role_id))
    except Exception as e:
        raise e


@event.listens_for(RevokedToken, 'load')
def load_revoked_tokes(token, _):
    # token.revoked_tokens = revoked_token_table.select()
    pass


@event.listens_for(User, 'load')
def user_loaded(user, _):
    user.domain_events = []
