#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from datetime import datetime
from typing import List, Union

from sqlalchemy import select, and_
from sqlalchemy.engine.row import RowProxy

from db_infrastructure import SqlQuery
from foundation import ThingGoneInBlackHoleError
from identity.adapters.identity_db import revoked_token_table, user_table, role_table, user_role_table
from identity.domain.entities import Role
from identity.domain.entities.user import UserStatus
from identity.domain.value_objects import ExceptionMessages, UserId, UserEmail
from web_app.serialization.dto import BaseTimeLoggedRequest, BaseAuthorizedRequest


@dataclass
class SimpleUserResponse:
    user_id: UserId
    email: UserEmail
    mobile: str
    profile_image: str
    last_login_at: datetime
    status: UserStatus
    created_at: datetime
    updated_at: datetime
    system_role: Role

    def serialize(self):
        return self.__dict__


class GetAllUsersQuery(abc.ABC):
    @abc.abstractmethod
    def query(self) -> List[SimpleUserResponse]:
        raise NotImplementedError


@dataclass
class GetSingleUserRequest(BaseTimeLoggedRequest):
    email: str


@dataclass
class GetCurrentUserRequest(BaseAuthorizedRequest):
    ...


class GetSingleUserQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: Union[GetSingleUserRequest, GetCurrentUserRequest]) -> SimpleUserResponse:
        raise NotImplementedError


class CountRevokedTokenByJTIQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, jti: str) -> bool:
        raise NotImplementedError


def _row_to_simple_user_dto(user_proxy: RowProxy) -> SimpleUserResponse:
    return SimpleUserResponse(
        user_id=user_proxy.user_id,
        email=user_proxy.email,
        mobile=user_proxy.mobile,
        profile_image=user_proxy.profile_image if hasattr(user_proxy, 'profile_image') else '',
        last_login_at=user_proxy.last_login_at,
        status=user_proxy.status,
        created_at=user_proxy.created_at,
        updated_at=user_proxy.updated_at,
        system_role=user_proxy.system_role.name,
    )


class SqlGetAllUsersQuery(GetAllUsersQuery, SqlQuery):
    def query(self) -> List[SimpleUserResponse]:
        return [
            _row_to_simple_user_dto(row) for row in self._conn.execute(user_table.select())
        ]


class SqlGetSingleUserQuery(GetSingleUserQuery, SqlQuery):
    def query(self, dto: Union[GetCurrentUserRequest, GetSingleUserRequest]) -> SimpleUserResponse:
        query = select([user_table, role_table.c.name.label('system_role')]) \
            .select_from(user_table) \
            .join(user_role_table, user_table.c.user_id == user_role_table.c.user_id) \
            .join(role_table, role_table.c.role_id == user_role_table.c.role_id) \
            .where(user_table.c.status == UserStatus.NORMAL)

        if isinstance(dto, GetCurrentUserRequest):
            query = query.where(user_table.c.user_id == dto.current_user_id)
        elif isinstance(dto, GetSingleUserRequest):
            query = query.where(user_table.c.email == dto.email)
        else:
            raise TypeError(ExceptionMessages.BAD_REQUEST)

        row = self._conn.execute(query).first()
        if row:
            return _row_to_simple_user_dto(row)

        raise ThingGoneInBlackHoleError(ExceptionMessages.USER_NOT_FOUND)


class SqlCountRevokedTokenByJTIQuery(CountRevokedTokenByJTIQuery, SqlQuery):
    def query(self, jti: str) -> bool:
        cnt = self._conn.execute(
            revoked_token_table.select().where(
                revoked_token_table.c.jti == jti
            )
        ).count()

        return cnt
