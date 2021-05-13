#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from typing import List, Union
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.engine.row import RowProxy

from auctions_infrastructure.queries.base import SqlQuery
from auth.adapters.identity_db import user_table
from auth.domain.entities import User
from auth.domain.value_objects import UserEmail, UserId


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
    def query(self, user_q: Union[UserId, UserEmail]) -> UserDto:
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
            user_table.select().where(
                or_(user_table.c.id == user_q, user_table.c.username == user_q)
            )
        ).first()
        return _row_to_dto(row)
