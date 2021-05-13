from dataclasses import dataclass

import pytest
from flask import testing

from auth.domain.value_objects import UserId
from web_app.tests.models import CreatingUserRequestFactory


def test_register_returns_details_with_auth_token(client: testing.FlaskClient) -> None:
    user_dto = CreatingUserRequestFactory.build()
    response = client.post("/user/register", json=user_dto.__dict__)

    assert response.status_code == 201
    json_response_body = response.json.copy()

    assert 'access_token' in json_response_body
    assert 'refresh_token' in json_response_body
    assert 'email' in json_response_body
    assert 'id' in json_response_body

    assert json_response_body['access_token'] is not None
    assert json_response_body['refresh_token'] is not None
    assert json_response_body['email'] == user_dto.email
    assert json_response_body['id'] is not None


@dataclass
class RegisteredUser:
    email: str
    password: str
    id: UserId


@pytest.fixture()
def registered_user(client: testing.FlaskClient) -> RegisteredUser:
    user_dto = CreatingUserRequestFactory.build()
    response = client.post("/user/register", json=user_dto.__dict__)
    return RegisteredUser(
        email=user_dto.email, password=user_dto.password, id=UserId(response.json['id'])
    )


def test_login(client: testing.FlaskClient, registered_user: RegisteredUser) -> None:
    response = client.post("/user/login",
                           json={"username": registered_user.email, "password": registered_user.password})

    assert response.status_code == 200
    json_response_body = response.json.copy()

    assert 'access_token' in json_response_body
    assert 'refresh_token' in json_response_body
    assert 'username' in json_response_body
    assert 'id' in json_response_body

    assert json_response_body['access_token'] is not None
    assert json_response_body['refresh_token'] is not None
    assert json_response_body['username'] == registered_user.email
    assert json_response_body['id'] is not None
