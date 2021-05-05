#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from foundation.events import Event
from product_catalog.catalog.src.domain.value_objects import CatalogReference, CatalogId, CollectionReference


@dataclass(frozen=True)
class CatalogCreated(Event):
    catalog_id: CatalogId
    reference: CatalogReference


@dataclass(frozen=True)
class CollectionCreated(Event):
    reference: CollectionReference
    catalog_id: CatalogId
    catalog_reference: CatalogReference
