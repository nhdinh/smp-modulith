#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

setup(
    name='product_catalog_infrastructure',
    version="0.0.0",
    packages=find_packages(),
    install_requires=['injector', 'sqlalchemy', 'foundation', 'auth', 'db_infrastructure'],
    extras_require={'dev': ['pytest']}
)