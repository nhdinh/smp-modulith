#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
import string
from datetime import datetime

import factory
import nanoid
from flask import testing

from store.application.usecases.product.create_store_product_uc import AddingShopProductRequest
from web_app.tests.shop.models import CreatedShopAndAccount


class AddingShopProductRequestFactory(factory.Factory):
    class Meta:
        model = AddingShopProductRequest

    shop_id = ''
    partner_id = ''
    timestamp = datetime.now().timestamp()

    title = factory.Faker('name')
    sku = factory.LazyFunction(lambda: nanoid.generate(string.ascii_letters + string.digits, 10))
    default_unit = 'Pcs'


class AddingShopProductRequestWithCatalogFactory(AddingShopProductRequestFactory):
    catalog = factory.LazyFunction(lambda: nanoid.generate(string.ascii_letters, 10))


def test_create_new_product(client: testing.FlaskClient, created_shop: CreatedShopAndAccount, authorized_shop_manager):
    product_dto = AddingShopProductRequestFactory.build()  # type: AddingShopProductRequest
    product_dto.shop_id = created_shop.shop_id

    response = client.post('/shop/product/add', json=product_dto.__dict__, headers=authorized_shop_manager)

    assert response.status_code == 201
    assert 'product_id' in response.json

    response = client.post('/shop/product/get',
                           json={"product_id": response.json['product_id'],
                                 "shop_id": created_shop.shop_id,
                                 "timestamp": datetime.now().timestamp()},
                           headers=authorized_shop_manager)

    assert response.status_code == 200
    assert 'catalog' in response.json
    assert 'catalog_id' in response.json['catalog']
    assert 'catalog_title' in response.json['catalog']


def test_create_new_product_with_catalog(client: testing.FlaskClient, created_shop: CreatedShopAndAccount,
                                         authorized_shop_manager):
    product_dto = AddingShopProductRequestWithCatalogFactory.build()  # type: AddingShopProductRequest
    product_dto.shop_id = created_shop.shop_id

    response = client.post('/shop/product/add', json=product_dto.__dict__, headers=authorized_shop_manager)

    assert response.status_code == 201
    assert 'product_id' in response.json

    response = client.post('/shop/product/get',
                           json={"product_id": response.json['product_id'],
                                 "shop_id": created_shop.shop_id,
                                 "timestamp": datetime.now().timestamp()},
                           headers=authorized_shop_manager)

    assert response.status_code == 200
    assert 'catalog' in response.json
    assert 'catalog_id' in response.json['catalog']
    assert 'catalog_title' in response.json['catalog']
    assert response.json['catalog']['catalog_title'] == product_dto.catalog
