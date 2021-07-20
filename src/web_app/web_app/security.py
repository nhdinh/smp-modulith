from typing import Any, Optional

from flask import Flask, request
from flask_security import Security
from flask_security.datastore import UserDatastore
from sqlalchemy.orm import Session

__all__ = ["setup", "User"]

from identity.domain.entities import Role, User


class SaUserDatastore(UserDatastore):
    def get_user(self, identifier: Any) -> Optional[User]:
        try:
            email = str(identifier)
        except (ValueError, TypeError):
            return None
        else:
            return self.session.query(User).filter(User.email == email).one_or_none()

    def find_user(self, **kwargs: dict) -> User:
        return self.session.query(User).filter_by(**kwargs).one()

    def put(self, model: User) -> User:
        self.session.add(model)
        return model

    def delete(self, model: User) -> None:
        self.session.delete(model)

    def commit(self) -> None:
        self.session.commit()

    def find_role(self, *args, **kwargs) -> None:  # type: ignore
        raise NotImplementedError

    @property
    def session(self) -> Session:
        return request.session  # type: ignore


user_datastore = SaUserDatastore(User, Role)


def setup(app: Flask) -> None:
    if 'SECURITY_REGISTERABLE' not in app.config.keys():
        app.config['SECURITY_REGISTERABLE'] = True

    if 'SECURITY_TRACKABLE' not in app.config.keys():
        app.config['SECURITY_TRACKABLE'] = True

    Security().init_app(app, user_datastore)
