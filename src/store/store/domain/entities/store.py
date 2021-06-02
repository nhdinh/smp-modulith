#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import Set

from foundation.entity import Entity
from foundation.events import EventMixin
from store.domain.entities.setting import Setting


class Store(EventMixin, Entity):
    def __init__(self):
        super().__init__()

        self.name = ''
        self._settings = set()  # type:Set[Setting]

    @property
    def settings(self) -> Set[Setting]:
        return self._settings
