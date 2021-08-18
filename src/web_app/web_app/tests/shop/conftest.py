#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from sqlite3 import Connection

import pytest
from flask import testing
from sqlalchemy import select
from store.adapter.shop_db import shop_registration_table
from store.application.usecases.initialize.register_shop_uc import RegisteringShopRequest
from store.domain.entities.registration_status import RegistrationStatus

from web_app.tests.shop.models import CreatedShopAndAccount, CreatedShopRegistration, RegisteringShopRequestFactory


@pytest.fixture
def created_registration(client: testing.FlaskClient) -> CreatedShopRegistration:
    shop_registration_dto = RegisteringShopRequestFactory.build()  # type: RegisteringShopRequest
    response = client.post('/shop/register', json=shop_registration_dto.__dict__)
    return CreatedShopRegistration(
        email=shop_registration_dto.email,
        password=shop_registration_dto.password,
        registration_id=response.json['registration_id'],
        confirmation_token=''
    )


@pytest.fixture
def created_shop(client: testing.FlaskClient, created_registration: CreatedShopRegistration,
                 connection: Connection) -> CreatedShopAndAccount:
    row = connection.execute(
        select([shop_registration_table.c.confirmation_token, shop_registration_table.c.status]).where(
            shop_registration_table.c.registration_id == created_registration.registration_id)).first()

    assert row is not None
    assert row['status'] == RegistrationStatus.REGISTRATION_WAITING_FOR_CONFIRMATION

    token = row['confirmation_token']
    response = client.post('/shop/confirm',
                           json={'confirmation_token': token, 'timestamp': datetime.now().timestamp()})

    assert response.status_code == 201

    return CreatedShopAndAccount(
        email=created_registration.email,
        password=created_registration.password,
        shop_id=response.json['shop_id']
    )


@pytest.fixture(scope='function')
def authorized_shop_manager(client: testing.FlaskClient, created_shop: CreatedShopAndAccount):
    response = client.post('/user/login', json={'username': created_shop.email, 'password': created_shop.password})
    assert 'access_token' in response.json
    access_token = response.json['access_token']
    headers = {
        'Authorization': 'Bearer {}'.format(access_token)
    }

    yield headers  # , created_shop.shop_id
