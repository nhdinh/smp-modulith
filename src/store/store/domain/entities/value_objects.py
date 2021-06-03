#!/usr/bin/env python
# -*- coding: utf-8 -*-
from uuid import UUID

from typing import NewType

StoreId = NewType("StoreId", tp=UUID)
