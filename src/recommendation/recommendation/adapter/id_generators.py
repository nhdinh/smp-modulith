#!/usr/bin/env python
# -*- coding: utf-8 -*-

from db_infrastructure import nanoid_generate

GROUP_ID_PREFIX = 'Rec'


def generate_recommend_group_id():
    return nanoid_generate(prefix=GROUP_ID_PREFIX)
