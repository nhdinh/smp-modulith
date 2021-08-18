#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

setup(
  name='inventory',
  version='0.0.0',
  packages=find_packages(),
  install_requires=['injector', 'sqlalchemy', 'foundation', 'db_infrastructure', 'identity', 'shop'],
  extras_require={'dev': ['pytest']}
)
