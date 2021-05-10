#!/usr/bin/env python
# -*- coding: utf-8 -*-
import factory
from faker.utils.text import slugify
from flask.testing import FlaskClient

from product_catalog import CatalogReference
from product_catalog.application.usecases.create_collection import CreatingCollectionRequest


class CreatingCollectionRequestFactory(factory.Factory):
    class Meta:
        model = CreatingCollectionRequest

    display_name = factory.Faker('name')
    reference = factory.LazyAttribute(lambda t: slugify(t.display_name))


def test_creating_collection_failed_unauthorized(client: FlaskClient, example_catalog: CatalogReference) -> None:
    dto = CreatingCollectionRequestFactory.build(catalog_reference=example_catalog)
    json_data = dto.__dict__
    response = client.post(f'/catalog/{example_catalog}/collections', json=json_data)

    assert response.status_code == 403


def test_creating_collection_success(example_catalog: CatalogReference, logged_in_client: FlaskClient) -> None:
    dto = CreatingCollectionRequestFactory.build(catalog_reference=example_catalog)
    json_data = dto.__dict__
    response = logged_in_client.post(f'/catalog/{example_catalog}/collections', json=json_data)

    assert response.status_code == 201

    assert 'reference' in response.json
    assert response.json['reference'] == json_data['reference']
