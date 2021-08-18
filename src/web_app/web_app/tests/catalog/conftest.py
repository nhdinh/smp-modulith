#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector
import pytest

from main.modules import RequestScope
from product_catalog import CatalogReference, MakeTestSampleCatalogUC
from product_catalog.application.usecases.begin_catalog import DefaultCatalog, MakeDefaultCatalogUC
from product_catalog.domain.entities.catalog import Catalog
from web_app.tests.catalog.models import TestSampleCatalogFactory


@pytest.fixture()
def example_catalog(container: injector.Injector) -> CatalogReference:
    with container.get(RequestScope):
        uc = container.get(MakeTestSampleCatalogUC)
        dto = TestSampleCatalogFactory.build()
        uc.execute(dto)

    return str(dto.reference)


@pytest.fixture()
def default_catalog(container: injector.Injector) -> Catalog:
    with container.get(RequestScope):
        uc = container.get(MakeDefaultCatalogUC)
        dto = DefaultCatalog()
        uc.execute(dto)

    return dto
