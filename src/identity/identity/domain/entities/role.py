#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from enum import Enum


class SystemRoleEnum(Enum):
    SystemAdmin = 0
    SystemUser = 1


@dataclass
class Role:
    name: SystemRoleEnum
    description: str

    def __hash__(self):
        return hash(self.name)

    @property
    def role_name(self) -> str:
        return self.name.name

    @property
    def role_value(self) -> int:
        return self.name.value
