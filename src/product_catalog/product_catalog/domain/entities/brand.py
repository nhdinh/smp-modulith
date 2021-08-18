#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import datetime


@dataclass(unsafe_hash=True)
class Brand:
  reference: str
  display_name: str
  created_at: datetime = datetime.now()
  disabled: bool = False
