#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Set

from foundation.entity import Entity
from foundation.events import EventMixin
from store.domain.entities.setting import Setting


class Store(EventMixin, Entity):
    def __init__(self):
        super(Store, self).__init__()

        self.store_id = ''
        self.name = ''
        self._settings: Set[Setting] = set()

    @property
    def settings(self) -> Set[Setting]:
        return self._settings
