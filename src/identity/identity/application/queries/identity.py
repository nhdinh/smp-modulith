#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from typing import List, Union
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.engine.row import RowProxy

from auctions_infrastructure.queries.base import SqlQuery
from identity.adapters.identity_db import user_table, revoked_token_table
from identity.domain.value_objects import UserEmail, UserId


@dataclass
class UserDto:
    id: UUID
    email: str


class GetAllUsersQuery(abc.ABC):
    @abc.abstractmethod
    def query(self) -> List[UserDto]:
        raise NotImplementedError


class GetSingleUserQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, user_q: UserEmail) -> UserDto:
        raise NotImplementedError


class CountRevokedTokenByJTIQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, jti: str) -> bool:
        raise NotImplementedError


def _row_to_dto(user_proxy: RowProxy) -> UserDto:
    return UserDto(
        id=user_proxy.id,
        email=user_proxy.email,
    )


class SqlGetAllUsersQuery(GetAllUsersQuery, SqlQuery):
    def query(self) -> List[UserDto]:
        return [
            _row_to_dto(row) for row in self._conn.execute(user_table.select())
        ]


class SqlGetSingleUserQuery(GetSingleUserQuery, SqlQuery):
    def query(self, user_q: Union[UserId, UserEmail]) -> UserDto:
        row = self._conn.execute(
            user_table.select().where(user_table.c.email == user_q)
        ).first()
        return _row_to_dto(row)


class SqlCountRevokedTokenByJTIQuery(CountRevokedTokenByJTIQuery, SqlQuery):
    def query(self, jti: str) -> bool:
        cnt = self._conn.execute(
            revoked_token_table.select().where(
                revoked_token_table.c.jti == jti
            )
        ).count()

        return cnt
