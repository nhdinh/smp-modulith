#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from foundation import Event
from store.domain.entities.value_objects import StoreId, StoreCatalogId


@dataclass(frozen=True)
class StoreCatalogCreatedEvent(Event):
    store_id: StoreId
    catalog_id: StoreCatalogId
    catalog_reference: str


@dataclass(frozen=True)
class StoreCatalogUpdatedEvent(Event):
    store_id: StoreId
    catalog_id: StoreCatalogId
    catalog_reference: str


@dataclass(frozen=True)
class StoreCatalogToggledEvent(Event):
    store_id: StoreId
    catalog_id: StoreCatalogId
    catalog_reference: str
    disabled: bool
