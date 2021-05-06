#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='product_catalog',
    version="0.0.0",
    packages=find_packages(),
    install_requires=['injector', 'sqlalchemy', 'foundation', 'db_infrastructure', 'product_catalog_infrastructure'],
    extras_require={'dev': ['pytest']}
)
