#!/usr/bin/env python
# -*- coding: utf-8 -*-
from db_infrastructure import nanoid_generate


def generate_user_id():
    return nanoid_generate(prefix='User')


def role_id_generator():
    return nanoid_generate(prefix='Role')
