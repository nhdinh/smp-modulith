#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from foundation.events import Event
from product_catalog.domain.value_objects import CatalogReference


@dataclass(frozen=True)
class CatalogCreatedEvent(Event):
    reference: CatalogReference
