#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass, field
from uuid import UUID

from typing import List
import marshmallow as ma


@dataclass
class StoreSettingResponseDto:
    name: str
    value: str
    type: str

    def serialize(self):
        return {
            'name': self.name,
            'value': self.value,
            'type': self.type,
        }


@dataclass
class StoreInfoResponseDto:
    store_id: UUID
    store_name: str
    # settings: List[StoreSettingResponseDto] = field(default_factory=list)
    settings: List[StoreSettingResponseDto] = field(metadata={"marshmallow_field": ma.fields.Raw()},
                                                    default_factory=list)

    def serialize(self):
        return {
            'store_id': str(self.store_id),
            'store_name': self.store_name,
            'settings': [setting.serialize() for setting in self.settings]
        }


class FetchStoreSettingsQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, store_of: str) -> StoreInfoResponseDto:
        pass


class CountStoreOwnerByEmailQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, email: str) -> int:
        pass
