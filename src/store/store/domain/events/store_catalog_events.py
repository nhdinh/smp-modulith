#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from foundation import Event


@dataclass(frozen=True)
class StoreCatalogUpdatedEvent(Event):
    catalog_reference: str
