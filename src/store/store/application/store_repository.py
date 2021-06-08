#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc

from repository import AbstractRepository
from store.domain.entities.store_registration import StoreRegistration
from store.domain.entities.store import Store
from store.domain.entities.value_objects import StoreId


class AbstractStoreRepository(AbstractRepository):
    def save(self, store: Store) -> None:
        self._save(store)

    @abc.abstractmethod
    def get(self, store: StoreId) -> Store:
        raise NotImplementedError


class SqlAlchemyStoreRepository(AbstractStoreRepository):
    def get(self, store_id_to_find: StoreId) -> Store:
        self._sess.query(Store).filter(Store.store_id == store_id_to_find).all()

    def _save(self, store: Store) -> None:
        self._sess.add(store)

    def save_registration(self, store_registration) -> None:
        self._sess.add(store_registration)

    def fetch_registration_by_token(self, token):
        return self._sess.query(StoreRegistration).filter(StoreRegistration.confirmation_token == token).first()
