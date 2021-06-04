#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc

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
    def get(self, store: StoreId) -> Store:
        raise NotImplementedError

    def save(self, store: Store) -> None:
        raise NotImplementedError

    def __init__(self, session: Session):
        self._sess = session  # type:Session
