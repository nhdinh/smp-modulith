#!/usr/bin/env python
# -*- coding: utf-8 -*-
from enum import Enum


class RecommendationTypes(Enum):
    EQUIVALENT = 'EQUIVALENT',
    EDITOR_PICKED = 'EDITOR_PICKED',
    CUSTOMER_PICKED = 'CUSTOMER_PICKED'
    CUSTOM = 'CUSTOM'
