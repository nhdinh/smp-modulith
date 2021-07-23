#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from typing import List, Union

from sqlalchemy import select
from sqlalchemy.engine.row import RowProxy

from db_infrastructure import SqlQuery
from foundation import ThingGoneInBlackHoleError
from identity.adapters.identity_db import revoked_token_table, user_table
from identity.domain.value_objects import ExceptionMessages
from inventory.domain.entities.value_objects import SystemUserId, SystemUserStatus
from web_app.serialization.dto import BaseTimeLoggedRequest, BaseAuthorizedRequest


@dataclass
class SimpleUserResponse:
    user_id: SystemUserId
    email: str
    status: SystemUserStatus

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
        status=user_proxy.status,
    )


class SqlGetAllUsersQuery(GetAllUsersQuery, SqlQuery):
    def query(self) -> List[SimpleUserResponse]:
        return [
            _row_to_simple_user_dto(row) for row in self._conn.execute(user_table.select())
        ]


class SqlGetSingleUserQuery(GetSingleUserQuery, SqlQuery):
    def query(self, dto: Union[GetCurrentUserRequest, GetSingleUserRequest]) -> SimpleUserResponse:
        if isinstance(dto, GetCurrentUserRequest):
            row = self._conn.execute(select(user_table).where(user_table.c.user_id == dto.current_user_id)).first()
        elif isinstance(dto, GetSingleUserRequest):
            row = self._conn.execute(select(user_table).where(user_table.c.email == dto.email)).first()
        else:
            raise TypeError(ExceptionMessages.BAD_REQUEST)

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
