#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from typing import NewType
from uuid import UUID

StoreCollectionId = NewType('StoreCollectionId', tp=UUID)
StoreCollectionReference = NewType('StoreCollectionReference', tp=str)


@dataclass(unsafe_hash=True)
class StoreCollection:
    reference: StoreCollectionReference
    title: str
    default: bool = False
    disabled: bool = False
    deleted: bool = False

    @property
    def catalog(self) -> 'StoreCatalog':
        return getattr(self, '_catalog')

    def __str__(self):
        return f'<StoreCollection #{self.collection_id} ref="{self.reference}" catalog="{self.catalog.title}">'

    def __eq__(self, other):
        if not other or not isinstance(other, StoreCollection):
            raise TypeError

        return self.reference == other.reference and self.title == other.title
