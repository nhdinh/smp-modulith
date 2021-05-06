#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import Optional

from product_catalog.domain.value_objects import CollectionReference


@dataclass(unsafe_hash=True)
class Collection:
    reference: Optional[CollectionReference]
    display_name: str
