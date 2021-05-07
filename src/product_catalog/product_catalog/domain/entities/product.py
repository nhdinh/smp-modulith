#!/usr/bin/env python
# -*- coding: utf-8 -*-
from foundation.events import EventMixin


class Product(EventMixin):
    def __init__(self):
        super().__init__()
