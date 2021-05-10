from dataclasses import dataclass

import pytest
from flask import testing
from sqlalchemy.engine import Connection

from customer_relationship import customers
from web_app.tests.models import CreatingUserRequestFactory


def test_register_returns_details_with_auth_token(client: testing.FlaskClient) -> None:
    user_dto = CreatingUserRequestFactory.build()
    response = client.post("/register", json=user_dto.__dict__)

    assert response.status_code == 200
    json_response_body = response.json.copy()
    assert isinstance(json_response_body["response"]["user"].pop("authentication_token"), str)
    assert isinstance(json_response_body["response"]["user"].pop("id"), str)
    assert json_response_body == {"meta": {"code": 200}, "response": {"user": {}}}


def test_register_creates_customer(client: testing.FlaskClient, connection: Connection) -> None:
    customer_dto = CreatingUserRequestFactory.build()
    response = client.post(
        "/register", json=customer_dto.__dict__
    )
    assert response.status_code == 200
    # if response.status_code != 200:
    #     pass

    assert_customer_with_given_email_exists(connection, customer_dto.email)


def assert_customer_with_given_email_exists(connection: Connection, email: str) -> None:
    assert connection.execute(customers.select().where(customers.c.email == email)).first()


@dataclass
class RegisteredUser:
    email: str
    password: str
    id: str


@pytest.fixture()
def registered_user(client: testing.FlaskClient) -> RegisteredUser:
    user_dto = CreatingUserRequestFactory.build()
    response = client.post("/register", json=user_dto.__dict__)
    client.cookie_jar.clear()
    return RegisteredUser(
        email=user_dto.email, password=user_dto.password, id=response.json["response"]["user"]["id"]
    )


def test_login(client: testing.FlaskClient, registered_user: RegisteredUser) -> None:
    response = client.post("/login", json={"email": registered_user.email, "password": registered_user.password})

    assert response.status_code == 200
    json_response_body = response.json.copy()
    json_response_body["response"]["user"].pop("authentication_token")
    assert json_response_body == {
        "meta": {"code": 200},
        "response": {"user": {"id": registered_user.id}},
    }
