#!/usr/bin/env python
# -*- coding: utf-8 -*-
import uuid

import factory
import injector
import pytest
from faker.utils.text import slugify
from flask import jsonify
from flask.testing import FlaskClient

from main.modules import RequestScope
from product_catalog import TestSampleCatalog, MakeTestSampleCatalogUC
from product_catalog.application.uc.create_catalog import CreatingCatalogRequest
from product_catalog.domain.value_objects import CatalogReference


class TestSampleCatalogFactory(factory.Factory):
    class Meta:
        model = TestSampleCatalog

    id = uuid.uuid4()
    reference = factory.LazyAttribute(lambda t: slugify(t.display_name))
    display_name = factory.Faker('name')


class CreatingCatalogRequestFactory(factory.Factory):
    class Meta:
        model = CreatingCatalogRequest

    display_name = factory.Faker('name')
    reference = factory.LazyAttribute(lambda t: slugify(t.display_name))


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
        uc = container.get(MakeTestSampleCatalogUC)
        dto = TestSampleCatalogFactory.build()
        uc.execute(dto)

    return str(dto.reference)


def test_return_single_catalog(client: FlaskClient, example_catalog: CatalogReference) -> None:
    response = client.get(f'/catalog/{example_catalog}', headers={'Content-Type': 'application/json'})
    assert response.status_code == 200
    assert type(response.json) == dict
    assert response.json['reference'] == example_catalog


def test_creating_catalog_failed_unauthorized(client: FlaskClient) -> None:
    dto = CreatingCatalogRequestFactory.build()
    json_data = dto.__dict__
    response = client.post('/catalog', json=json_data)

    assert response.status_code == 403


def test_creating_catalog_success(logged_in_client: FlaskClient) -> None:
    dto = CreatingCatalogRequestFactory.build()
    json_data = dto.__dict__
    response = logged_in_client.post('/catalog', json=json_data)

    assert response.status_code == 201

    assert 'id' in response.json
    assert response.json['id'] is not None

    assert 'reference' in response.json
    assert response.json['reference'] == dto.reference


def test_creating_catalog_failed_with_duplicate_reference(logged_in_client: FlaskClient,
                                                          example_catalog: CatalogReference) -> None:
    dto = CreatingCatalogRequestFactory.build()
    dto.reference = example_catalog
    response = logged_in_client.post('/catalog', json=dto.__dict__)

    assert response.status_code == 400
    assert response.json['messages'] == ['Catalog has been existed']
