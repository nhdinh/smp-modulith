#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc

from store.domain.entities.store import Store
from store.domain.value_objects import StoreID

from sqlalchemy.orm import Session


class AbstractStoreRepository(abc.ABC):
    @abc.abstractmethod
    def get(self, store: StoreID) -> Store:
        raise NotImplementedError

    @abc.abstractmethod
    def save(self, store: Store) -> None:
        raise NotImplementedError


class SqlAlchemyStoreRepository(AbstractStoreRepository):
    def __init__(self, session: Session):
        self._sess = session  # type:Session
