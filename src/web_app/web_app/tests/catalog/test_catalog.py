#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
from flask.testing import FlaskClient

from product_catalog.domain.value_objects import CatalogReference
from web_app.tests.catalog.models import CreatingCatalogRequestFactory


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


def test_creating_catalog_success(
        logged_in_client: FlaskClient
) -> None:
    dto = CreatingCatalogRequestFactory.build()
    json_data = dto.__dict__
    response = logged_in_client.post('/catalog', json=json_data)

    assert response.status_code == 201

    assert 'reference' in response.json
    assert response.json['reference'] == dto.reference


def test_creating_catalog_failed_with_duplicate_reference(
        logged_in_client: FlaskClient,
        example_catalog: CatalogReference
) -> None:
    dto = CreatingCatalogRequestFactory.build()
    dto.reference = example_catalog

    with pytest.raises(Exception):
        response = logged_in_client.post('/catalog', json=dto.__dict__)

        assert response.status_code == 400
        # assert 'Catalog has been existed' in response.json['messages']
        assert 'UNIQUE constraint failed: catalog.reference' in response.json['messages']
