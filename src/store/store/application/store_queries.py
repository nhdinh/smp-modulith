#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from uuid import UUID


@dataclass
class StoreSettingsDto:
    name: str
    value: str

    def serialize(self):
        return {
            'name': self.name,
            'value': self.value,
        }


class FetchStoreSettingsQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, store_of: str) -> StoreSettingsDto:
        pass
