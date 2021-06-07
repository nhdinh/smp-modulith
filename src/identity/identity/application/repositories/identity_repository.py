#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from typing import List, Union

from identity.domain.entities import Role, User
from identity.domain.value_objects import UserId, UserEmail
from repository import AbstractRepository


class AbstractIdentityRepository(AbstractRepository):
    @abc.abstractmethod
    def fetch_user(self, query: Union[UserId, UserEmail]) -> User:
        raise NotImplementedError


class SqlAlchemyIdentityRepository(AbstractIdentityRepository):
    def fetch_user(self, query: UserEmail) -> User:
        return self._fetch_user_by_email(email=query)

    def _fetch_user_by_id(self, user_id: UserId) -> User:
        return self._sess.query(User).filter(User.id == user_id).first()

    def _fetch_user_by_email(self, email: UserEmail) -> User:
        return self._sess.query(User).filter(User.email == email).first()

    def _save(self, user: User) -> None:
        self._sess.add(user)

    def get_roles(self) -> List[Role]:
        return self._sess.query(Role).all()

    def add_revoked_token(self, token):
        return self._sess.add(token)
