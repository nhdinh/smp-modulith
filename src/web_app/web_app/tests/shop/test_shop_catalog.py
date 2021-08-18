#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from sqlite3 import Connection

import factory
from flask import testing
from sqlalchemy import select
from store.adapter.shop_db import shop_registration_table
from store.application.usecases.catalog.create_store_catalog_uc import AddingShopCatalogRequest
from store.domain.entities.registration_status import RegistrationStatus

from web_app.tests.shop.conftest import CreatedShopRegistration, RegisteringShopRequestFactory
from web_app.tests.shop.models import CreatedShopAndAccount


def test_register_new_shop(client: testing.FlaskClient):
  shop_registration_dto = RegisteringShopRequestFactory.build()
  response = client.post('/shop/register', json=shop_registration_dto.__dict__)

  assert response.status_code == 201
  assert 'request_id' in response.json
  assert 'registration_id' in response.json


def test_confirm_shop_registration(client: testing.FlaskClient, connection: Connection,
                                   created_registration: CreatedShopRegistration):
  row = connection.execute(
    select([shop_registration_table.c.confirmation_token, shop_registration_table.c.status]).where(
      shop_registration_table.c.registration_id == created_registration.registration_id)).first()

  assert row is not None
  assert row['status'] == RegistrationStatus.REGISTRATION_WAITING_FOR_CONFIRMATION

  token = row['confirmation_token']
  response = client.post('/shop/confirm',
                         json={'confirmation_token': token, 'timestamp': datetime.now().timestamp()})

  assert response.status_code == 201
  assert 'shop_id' in response.json


class CreatingShopCatalogRequestFactory(factory.Factory):
  class Meta:
    model = AddingShopCatalogRequest

  name = factory.Faker('name')
  shop_id = ''
  partner_id = ''
  timestamp = datetime.now().timestamp()


def test_shop_create_catalog(client: testing.FlaskClient, created_shop: CreatedShopAndAccount,
                             authorized_shop_manager):
  catalog_dto = CreatingShopCatalogRequestFactory.build()  # type:AddingShopCatalogRequest
  catalog_dto.shop_id = created_shop.shop_id

  response = client.post('/shop/catalog/add', json=catalog_dto.__dict__, headers=authorized_shop_manager)

  assert response.status_code == 201
  assert 'catalog_id' in response.json
  assert response.json['catalog_id'] is not None
  # assert response.json['catalog_id'] is not None
