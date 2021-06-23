#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Set

from foundation import slugify
from store.application.usecases.const import ExceptionMessages

from store.domain.entities.value_objects import StoreCatalogReference


@dataclass(unsafe_hash=True)
class StoreCatalog:
    reference: StoreCatalogReference
    title: str
    display_image: str = ''
    disabled: bool = False
    default: bool = False
