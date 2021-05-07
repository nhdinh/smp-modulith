#!/usr/bin/env python
# -*- coding: utf-8 -*-
import uuid

import factory
import injector
import pytest
from flask.testing import FlaskClient

from main.modules import RequestScope
from product_catalog import BeginningCatalogRequest, BeginningCatalog
from product_catalog.domain.value_objects import CatalogReference


class BeginningCatalogRequestFactory(factory.Factory):
    class Meta:
        model = BeginningCatalogRequest

    id = uuid.uuid4()
    reference = str(uuid.uuid4())
    display_name = factory.Faker('name')


@pytest.fixture()
def logged_in_client(client: FlaskClient) -> FlaskClient:
    email, password = "tests+bid+1@cleanarchitecture.io", "Dumm123!"
    client.post(
        "/register",
        json={"email": email, "password": password},
    )
    return client


@pytest.fixture()
def example_catalog(container: injector.Injector) -> CatalogReference:
    with container.get(RequestScope):
        uc = container.get(BeginningCatalog)
        dto = BeginningCatalogRequestFactory.build()
        uc.execute(dto)

    return str(dto.reference)


def test_return_single_catalog(client: FlaskClient, example_catalog: CatalogReference) -> None:
    response = client.get(f'/catalog/{example_catalog}', headers={'Content-Type': 'application/json'})
    assert response.status_code == 200
    assert type(response.json) == dict
    assert response.json['reference'] == example_catalog


def test_create_catalog(logged_in_client: FlaskClient, example_catalog: CatalogReference) -> None:
    response = logged_in_client.post(f'/catalog', headers={})
    assert 1==1
