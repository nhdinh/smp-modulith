#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from typing import List, Union

from foundation.repository import AbstractRepository

from identity.domain.entities import Role, User
from identity.domain.value_objects import UserEmail, UserId


class AbstractIdentityRepository(AbstractRepository):
    @abc.abstractmethod
    def get_user(self, query: Union[UserId, UserEmail]) -> User:
        raise NotImplementedError


class SqlAlchemyIdentityRepository(AbstractIdentityRepository):
    def get_user(self, query: UserEmail) -> User:
        return self._get_user_by_email(email=query)

    def get_user_by_id(self, user_id: UserId) -> User:
        return self._sess.query(User).filter(User.user_id == user_id).first()

    def _get_user_by_email(self, email: UserEmail) -> User:
        return self._sess.query(User).filter(User.email == email).first()

    def _save(self, user: User) -> None:
        self._sess.add(user)

    def get_roles(self) -> List[Role]:
        return self._sess.query(Role).all()

    def add_revoked_token(self, token: str):
        return self._sess.add(token)

    def fetch_user_by_token(self, reset_password_token: str):
        return self._sess.query(User).filter(User.reset_password_token == reset_password_token).first()
