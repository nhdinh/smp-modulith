#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from datetime import datetime
from typing import List, Union, Optional

from foundation.repository import AbstractRepository
from identity.domain.entities import Role, User
from identity.domain.entities.role import SystemRoleEnum
from identity.domain.entities.user import UserStatus
from identity.domain.value_objects import UserEmail, UserId


class AbstractIdentityRepository(AbstractRepository):
  @abc.abstractmethod
  def get_active_user(self, query: Union[UserId, UserEmail]) -> User:
    raise NotImplementedError


class SqlAlchemyIdentityRepository(AbstractIdentityRepository):
  def get_active_user(self, query: UserEmail) -> User:
    user = self._get_user_by_email(email=query, active_only=True)
    return user

  def get_user_by_id(self, user_id: UserId, active_only: bool) -> User:
    selector = self._sess.query(User).filter(User.user_id == user_id)
    if active_only:
      selector = selector.filter(User.status == UserStatus.NORMAL)

    user = selector.first()
    user = self._user_first_login(user)
    return user

  def _get_user_by_email(self, email: UserEmail, active_only: bool) -> User:
    selector = self._sess.query(User).filter(User.email == email)
    if active_only:
      selector = selector.filter(User.status == UserStatus.NORMAL)

    user = selector.first()
    user = self._user_first_login(user)
    return user

  def _save(self, user: User) -> None:
    self._sess.add(user)

  def get_roles(self) -> List[Role]:
    return self._sess.query(Role).all()

  def add_revoked_token(self, token: str):
    return self._sess.add(token)

  def fetch_user_by_token(self, reset_password_token: str):
    return self._sess.query(User).filter(User.reset_password_token == reset_password_token).first()

  def _user_first_login(self, user: User) -> Optional[User]:
    # return user if user is None
    if user is None:
      return None

    user.failed_login_count = user.failed_login_count or 0
    user.last_login_at = user.last_login_at or datetime.now()
    if not user.system_role:
      system_user_role = self._sess.query(Role).filter(Role.name == SystemRoleEnum.SystemUser).first()
      user.system_role = system_user_role

    return user
