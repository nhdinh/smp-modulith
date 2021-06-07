#!/usr/bin/env python
# -*- coding: utf-8 -*-
import decimal
from dataclasses import dataclass

from typing import Type, Any


@dataclass(unsafe_hash=True)
class Setting:
    name: str
    value: str
    type: str

    def get_value(self) -> Any:
        if self.type == 'int':
            return int(self.value)
        elif self.type == 'decimal' or self.type == 'float':
            return float(self.value)
        elif self.type == 'str':
            return self.value
        else:
            return self.value
