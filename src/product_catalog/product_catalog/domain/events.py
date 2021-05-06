#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from foundation.events import Event
from product_catalog.domain.value_objects import CatalogId, CatalogReference, CollectionReference


@dataclass(frozen=True)
class CatalogCreated(Event):
    catalog_id: CatalogId
    reference: CatalogReference


@dataclass(frozen=True)
class CollectionCreatedEvent(Event):
    reference: CollectionReference
    catalog_id: CatalogId
    catalog_reference: CatalogReference
