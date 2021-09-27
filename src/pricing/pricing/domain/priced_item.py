#!/usr/bin/env python
# -*- coding: utf-8 -*-
from foundation import EventMixin
from pricing.domain.value_objects import GenericItemStatus


class PricedItem(EventMixin):
    def __init__(self, product_id, title, status: GenericItemStatus = GenericItemStatus.NORMAL, version: int = 0):
        super(PricedItem, self).__init__()

        self.title = title
        self.status = status
        self.version = version
