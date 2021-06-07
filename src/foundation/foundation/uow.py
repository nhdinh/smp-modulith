#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import abc
from typing import Optional

from sqlalchemy.orm import Session

from foundation.events import EventBus


class AbstractUnitOfWork(abc.ABC):
    def __enter__(self) -> AbstractUnitOfWork:
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self):
        self._commit()

    def collect_new_events(self):
        self._collect_new_events()

    @abc.abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError

    @abc.abstractmethod
    def _collect_new_events(self):
        raise NotImplementedError


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, sessionfactory, event_bus: EventBus):
        self._sf = sessionfactory
        self._session = None  # type:Optional[Session]
        self._event_bus = event_bus  # type:Optional[EventBus]

    def __exit__(self, *kwargs):
        super(SqlAlchemyUnitOfWork, self).__exit__(*kwargs)
        self._session.close()

    @abc.abstractmethod
    def _collect_new_events(self):
        raise NotImplementedError

    @property
    def session(self):
        return self._session
