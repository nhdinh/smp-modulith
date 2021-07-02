#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from store.domain.entities.store import StoreId


@dataclass(frozen=True)
class StoreRegistrationConfirmedEvent:
    store_id: StoreId
    store_name: str
