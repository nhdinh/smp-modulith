#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc

from store.domain.entities.store_registration import StoreRegistration

from foundation.events import EventBus, EventMixin
from store.domain.entities.store import Store
from store.domain.entities.value_objects import StoreId

from sqlalchemy.orm import Session


class AbstractStoreRepository(abc.ABC):
    @abc.abstractmethod
    def get(self, store: StoreId) -> Store:
        raise NotImplementedError

    @abc.abstractmethod
    def save(self, store: Store) -> None:
        raise NotImplementedError


class SqlAlchemyStoreRepository(AbstractStoreRepository):
    def __init__(self, session: Session, event_bus: EventBus):
        self._sess = session  # type:Session
        self._event_bus = event_bus

    def get(self, store: StoreId) -> Store:
        self._sess.query(Store).filter(Store.store_id == store).all()

    def save(self, store: Store) -> None:
        self._collect_events(store)
        self._sess.add(store)

    def save_registration(self, store_registration) -> None:
        self._collect_events(store_registration)
        self._sess.add(store_registration)

    def _collect_events(self, entity: EventMixin):
        for event in entity.domain_events:
            self._event_bus.post(event)

        entity.clear_events()

    def get_registration_by_token(self, token):
        return self._sess.query(StoreRegistration).filter(StoreRegistration.confirmation_token == token).first()
