#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from uuid import UUID


@dataclass
class StoreSettingsDto:
    name: str
    value: str
    type: str

    def serialize(self):
        return {
            'name': self.name,
            'value': self.value,
            'type': self.type,
        }


class FetchStoreSettingsQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, store_of: str) -> StoreSettingsDto:
        pass


class CountStoreOwnerByEmailQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, email: str) -> int:
        pass
