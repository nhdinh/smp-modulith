#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass


@dataclass(unsafe_hash=True)
class Role:
    name: str
    description: str
