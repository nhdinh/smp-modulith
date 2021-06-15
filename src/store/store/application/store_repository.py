#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from typing import Optional

from repository import AbstractRepository
from store.domain.entities.store import Store
from store.domain.entities.store_owner import StoreOwner
from store.domain.entities.store_registration import StoreRegistration
from store.domain.entities.value_objects import StoreId


class AbstractStoreRepository(AbstractRepository):
    def save(self, store: Store) -> None:
        self._save(store)

    @abc.abstractmethod
    def get(self, store: StoreId) -> Store:
        raise NotImplementedError


class SqlAlchemyStoreRepository(AbstractStoreRepository):
    def get(self, store_id_to_find: StoreId) -> Optional[Store]:
        return self._sess.query(Store).filter(Store.store_id == store_id_to_find).first()

    def _save(self, store: Store) -> None:
        self._sess.add(store)

    def save_registration(self, store_registration) -> None:
        self._sess.add(store_registration)

    def fetch_registration_by_token(self, token):
        return self._sess.query(StoreRegistration).filter(StoreRegistration.confirmation_token == token).first()

    def fetch_store_of_owner(self, owner: str) -> Store:
        """
        Fetch store of the owner
        :param owner:
        """
        return self._sess.query(Store).join(StoreOwner).filter(StoreOwner.email == owner).with_for_update().first()
