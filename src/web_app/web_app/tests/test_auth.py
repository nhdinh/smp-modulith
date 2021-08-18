from dataclasses import dataclass

import pytest
import sqlalchemy.exc
from flask import testing

from identity.domain.value_objects import UserId
from web_app.tests.models import CreatingLoginRequestFactory, CreatingUserRequestFactory


def test_register_returns_details_with_auth_token(client: testing.FlaskClient) -> None:
    user_dto = CreatingUserRequestFactory.build()
    response = client.post("/user/register", json=user_dto.__dict__)

    assert response.status_code == 201
    json_response_body = response.json.copy()

    assert 'access_token' in json_response_body
    assert 'refresh_token' in json_response_body
    # assert 'email' in json_response_body
    assert 'user_id' in json_response_body

    assert json_response_body['access_token'] is not None
    assert json_response_body['refresh_token'] is not None
    # assert json_response_body['email'] == user_dto.email
    assert json_response_body['user_id'] is not None


@dataclass
class RegisteredUser:
    email: str
    password: str
    user_id: UserId


@pytest.fixture()
def registered_user(client: testing.FlaskClient) -> RegisteredUser:
    user_dto = CreatingUserRequestFactory.build()
    response = client.post("/user/register", json=user_dto.__dict__)
    return RegisteredUser(
        email=user_dto.email, password=user_dto.password, user_id=UserId(response.json['user_id'])
    )


def test_registered_with_already_registered_user(client: testing.FlaskClient, registered_user: RegisteredUser):
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        response = client.post('/user/register', json={
            'email': registered_user.email,
            'password': 'S0mep@ss'
        })

        assert response.status_code == 400
        assert 'IntegrityError' in str(response.data)


def test_login(client: testing.FlaskClient, registered_user: RegisteredUser) -> None:
    response = client.post("/user/login",
                           json={"username": registered_user.email, "password": registered_user.password})

    assert response.status_code == 200
    json_response_body = response.json.copy()

    assert 'access_token' in json_response_body
    assert 'refresh_token' in json_response_body
    # assert 'username' in json_response_body
    assert 'user_id' in json_response_body

    assert json_response_body['access_token'] is not None
    assert json_response_body['refresh_token'] is not None
    # assert json_response_body['username'] == registered_user.email
    assert json_response_body['user_id'] is not None


def test_login_with_no_account(client: testing.FlaskClient) -> None:
    dto = CreatingLoginRequestFactory.build()

    with pytest.raises(Exception):
        response = client.post('/user/login', json=dto.__dict__)

        assert response.status_code == 400
        assert 'User not found' in str(response.data)
