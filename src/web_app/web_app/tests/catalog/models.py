#!/usr/bin/env python
# -*- coding: utf-8 -*-

import factory
from faker.utils.text import slugify

from product_catalog import TestSampleCatalog
from product_catalog.application.usecases.create_catalog import CreatingCatalogRequest


class TestSampleCatalogFactory(factory.Factory):
  class Meta:
    model = TestSampleCatalog

  reference = factory.LazyAttribute(lambda t: slugify(t.display_name))
  display_name = factory.Faker('name')


class CreatingCatalogRequestFactory(factory.Factory):
  class Meta:
    model = CreatingCatalogRequest

  name = factory.Faker('name')
