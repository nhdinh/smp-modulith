#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations
import abc
from typing import Optional

from injector import Injector
from sqlalchemy.orm import Session


class AbstractUnitOfWork(abc.ABC):
    def __enter__(self) -> AbstractUnitOfWork:
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self):
        self._commit()

    @abc.abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError

    def collect_new_events(self):
        self._collect_new_events()

    @abc.abstractmethod
    def _collect_new_events(self):
        raise NotImplementedError


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, sessionfactory):
        self._sf = sessionfactory
        self._session = None  # type:Optional[Session]

    def __enter__(self):
        self._session = self._sf()
        return super(SqlAlchemyUnitOfWork, self).__enter__()

    def __exit__(self, *kwargs):
        super(SqlAlchemyUnitOfWork, self).__exit__(*kwargs)
        self._session.close()

    def _commit(self):
        self._session.commit()

    def rollback(self):
        self._session.rollback()

    @abc.abstractmethod
    def _collect_new_events(self):
        raise NotImplementedError

    @property
    def session(self):
        return self._session


class InjectorUnitOfWork(SqlAlchemyUnitOfWork):
    def __init__(self, injector: Injector, sessionfactory) -> None:
        # TODO: check if do we need this class? This class is for what? Setup the injector?
        super(InjectorUnitOfWork, self).__init__(sessionfactory=sessionfactory)

        self._injector = injector

    @abc.abstractmethod
    def _collect_new_events(self):
        raise NotImplementedError
