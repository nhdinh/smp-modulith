#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import Any


@dataclass(unsafe_hash=True)
class Setting:
    key: str
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

    @property
    def shop(self):
        return getattr(self, '_shop')

    def __eq__(self, other):
        if not isinstance(other, Setting):
            raise TypeError

        return self.key == other.key and self.value == other.value
