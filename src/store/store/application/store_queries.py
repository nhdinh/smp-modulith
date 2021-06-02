#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from uuid import UUID


@dataclass
class StoreSettingsDto:
    store_id: UUID

    def serialize(self):
        return {
            'store_id': self.store_id,
        }


class FetchStoreSettingsQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, store_id: UUID) -> StoreSettingsDto:
        pass
