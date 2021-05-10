#!/usr/bin/env python
# -*- coding: utf-8 -*-
import factory
from faker.utils.text import slugify
from flask.testing import FlaskClient

from product_catalog import CatalogReference
from product_catalog.application.usecases.create_product import CreatingProductRequest
from product_catalog.domain.entities.catalog import Catalog


class CreatingProductRequestFactory(factory.Factory):
    class Meta:
        model = CreatingProductRequest

    display_name = factory.Faker('name')
    reference = factory.LazyAttribute(lambda t: slugify(t.display_name))


def test_creating_product_failed_unauthorized(client: FlaskClient, example_catalog: CatalogReference):
    product_dto = CreatingProductRequestFactory.build(catalog_reference=example_catalog)
    response = client.post(f'/product', json=product_dto.__dict__)

    assert response.status_code == 403  # unauthorized


def test_creating_product_failed_with_empty_display_name(logged_in_client: FlaskClient):
    product_dto = CreatingProductRequestFactory.build()
    json_data = product_dto.__dict__
    json_data['display_name'] = ''
    response = logged_in_client.post('/product', json=json_data)

    assert response.status_code == 400
    assert 'Display name must not be empty' in response.json['message']


def test_creating_product_success_with_only_display_name(logged_in_client: FlaskClient):
    product_dto = CreatingProductRequestFactory.build(reference='')
    response = logged_in_client.post('/product', json=product_dto.__dict__)

    assert response.status_code == 201

    assert 'product_id' in response.json
    assert response.json['product_id'] is not None

    assert 'reference' in response.json
    assert response.json['reference'] is not None
    assert response.json['reference'] == slugify(product_dto.display_name)


def test_creating_product_success_with_no_parent_will_set_default_collection(logged_in_client: FlaskClient,
                                                                             default_catalog: Catalog):
    product_dto = CreatingProductRequestFactory.build()
    response = logged_in_client.post('/product', json=product_dto.__dict__)

    assert response.status_code == 201

    assert 'product_id' in response.json
    assert response.json['product_id'] is not None
