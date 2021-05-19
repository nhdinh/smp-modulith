#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Dict

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

    assert response.status_code == 401


def test_creating_catalog_success(client: FlaskClient, authorized_headers: Dict) -> None:
    dto = CreatingCatalogRequestFactory.build()
    json_data = dto.__dict__
    response = client.post('/catalog', json=json_data, headers=authorized_headers)

    assert response.status_code == 201

    assert 'reference' in response.json
    assert response.json['reference'] == dto.reference


def test_creating_catalog_failed_with_duplicate_reference(client: FlaskClient, authorized_headers: Dict,
                                                          example_catalog: CatalogReference) -> None:
    dto = CreatingCatalogRequestFactory.build()
    dto.reference = example_catalog

    with pytest.raises(Exception):
        response = client.post('/catalog', json=dto.__dict__, headers=authorized_headers)

        assert response.status_code == 400
        # assert 'Catalog has been existed' in response.json['messages']
        assert 'UNIQUE constraint failed: catalog.reference' in response.json['messages']
