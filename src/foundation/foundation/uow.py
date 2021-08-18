#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import abc
from typing import Optional

from sqlalchemy import event
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


class SqlAlchemyUnitOfWork(AbstractUnitOfWork, abc.ABC):
    def __init__(self, sessionfactory, event_bus: EventBus):
        self.events = []
        self._sf = sessionfactory
        self._session = None  # type:Optional[Session]
        self._event_bus = event_bus  # type:Optional[EventBus]

    def __exit__(self, *args):
        super(SqlAlchemyUnitOfWork, self).__exit__(*args)
        self._session.close()

    @property
    def session(self):
        return self._session

    def __enter__(self) -> AbstractUnitOfWork:
        # make session
        if self._session is None:
            self._session = self._sf()  # type:Session

        @event.listens_for(self._session, 'after_commit')
        def receive_after_commit(session):
            """
            Add a hook to listen the event `after_commit`.
            After session is commited, this will receive all the processed entities, and then check if there is any
            domain_event that included in that such entity. Add it to the event stack automatically.
            """
            for processed_entity in session.identity_map.values():
                if hasattr(processed_entity, 'domain_events') and processed_entity.domain_events:
                    while processed_entity.domain_events:
                        domain_event = processed_entity.domain_events.pop(0)
                        self._event_bus.post(domain_event)

        return super(SqlAlchemyUnitOfWork, self).__enter__()

    def _collect_new_events(self):
        while self.events:
            yield self.events.pop(0)

    def _event_subscribe(self, domain_event):
        self.events.append(domain_event)
