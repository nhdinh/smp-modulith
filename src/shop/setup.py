#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

setup(
    name='shop',
    version='0.0.1',
    packages=find_packages(),
    install_requires=['injector', 'sqlalchemy', 'foundation', 'db_infrastructure', 'identity', 'product_catalog'],
    extras_require={'dev': ['pytest']}
)
