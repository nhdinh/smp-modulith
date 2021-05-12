#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc

from sqlalchemy.orm import Session
from typing import List, Union

from auth.domain.entities import Role, User
from auth.domain.value_objects import UserId, UserEmail


class AbstractIdentityRepository(abc.ABC):
    @abc.abstractmethod
    def fetch_user(self, query: Union[UserId, UserEmail]) -> User:
        raise NotImplementedError

    @abc.abstractmethod
    def save(self, user: User) -> None:
        raise NotImplementedError


class SqlAlchemyIdentityRepository(AbstractIdentityRepository):
    def fetch_user(self, query: Union[UserId, UserEmail]) -> User:
        if type(query) is UserId:
            return self._fetch_user_by_id(user_id=query)
        else:
            return self._fetch_user_by_email(email=query)

    def _fetch_user_by_id(self, user_id: UserId) -> User:
        return self._sess.query(User).filter(User.id == user_id).first()

    def _fetch_user_by_email(self, email: UserEmail) -> User:
        return self._sess.query(User).filter(User.email == email).first()

    def save(self, user: User) -> None:
        self._sess.add(user)

    def __init__(self, session: Session):
        self._sess = session  # type:Session

    def get_roles(self) -> List[Role]:
        return self._sess.query(Role).all()
