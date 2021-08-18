#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import List


@dataclass
class PaginationR1esponseDto:
    items: List
    current_page: int
    page_size: int
    total_items: int
    total_pages: int
