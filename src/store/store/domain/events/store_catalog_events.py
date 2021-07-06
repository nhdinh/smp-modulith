#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from foundation import Event
from store.domain.entities.value_objects import StoreId, StoreCatalogId, StoreCollectionId


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
class StoreCatalogDeletedEvent(Event):
    store_id: StoreId
    catalog_id: StoreCatalogId
    owner_name: str
    delete_completely: bool


@dataclass(frozen=True)
class StoreCatalogToggledEvent(Event):
    store_id: StoreId
    catalog_id: StoreCatalogId
    catalog_reference: str
    disabled: bool


@dataclass(frozen=True)
class StoreCollectionCreatedEvent(Event):
    store_id: StoreId
    catalog_id: StoreCatalogId
    collection_id: StoreCollectionId
    collection_reference: str


@dataclass(frozen=True)
class StoreCollectionToggledEvent(Event):
    store_id: StoreId
    catalog_id: StoreCatalogId
    collection_id: StoreCollectionId
    collection_reference: str
    disabled: bool


@dataclass(frozen=True)
class StoreCollectionUpdatedEvent(Event):
    store_id: StoreId
    catalog_id: StoreCatalogId
    collection_id: StoreCollectionId
    collection_reference: str
    disabled: bool


@dataclass(frozen=True)
class StoreCollectionDeletedEvent(Event):
    store_id: StoreId
    catalog_id: StoreCatalogId
    collection_id: StoreCollectionId
    collection_reference: str
