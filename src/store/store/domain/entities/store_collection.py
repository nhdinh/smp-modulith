#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass

from foundation import short_id
from store.domain.entities.value_objects import StoreCollectionReference


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
