import os
from typing import Dict

import injector
import pytest
from _pytest.tmpdir import TempPathFactory
from flask import Flask, testing
from flask.testing import FlaskClient
from sqlalchemy.engine import Connection, create_engine

from web_app.app import create_app
from web_app.tests.models import CreatingUserRequestFactory


@pytest.fixture(scope="session")
def config_path(tmp_path_factory: TempPathFactory) -> str:
    temp_dir = tmp_path_factory.mktemp("config")
    db_dir = tmp_path_factory.mktemp("test_db")
    conf_file_path = temp_dir / ".test_env_file"
    with open(conf_file_path, "w") as f:
        f.writelines(
            [
                "PAYMENTS_LOGIN=empty\n",
                "PAYMENTS_PASSWORD=empty\n",
                "EMAIL_HOST=localhost\n",
                "EMAIL_PORT=2525\n",
                "EMAIL_USERNAME=none\n",
                "EMAIL_PASSWORD=none\n",
                "EMAIL_FROM_NAME=Auctions\n",
                "EMAIL_FROM_ADDRESS=auctions@cleanarchitecture.io\n",
                "REDIS_HOST=localhost\n",
                f"DB_DSN=sqlite:///{db_dir}/db.sqlite\n",
                "MINIO_HOST=minio:9000\n",
                "MINIO_ACCESS_KEY=Q3AM3UQ867\n",
                "MINIO_SECRET_KEY=Vh5smyLeyCZd^$4m9pmb7T16!DwyU18kvPJFiCSG\n",
            ]
        )
    return str(conf_file_path)


@pytest.fixture(scope="session")
def app(config_path: str) -> Flask:
    os.environ["CONFIG_PATH"] = config_path
    # Disable password hashing in tests to get speed-up
    settings_to_override = {
        "SECURITY_PASSWORD_HASH": "plaintext",
        "SECURITY_HASHING_SCHEMES": ["hex_md5"],
        "SECURITY_DEPRECATED_HASHING_SCHEMES": [],
        "TESTING": True,
    }
    app = create_app(settings_to_override)
    yield app


@pytest.fixture()
def container(app: Flask) -> injector.Injector:
    return app.injector  # type: ignore


@pytest.fixture(scope='function')
def client(app: Flask) -> testing.FlaskClient:
    testclient = app.test_client()

    yield testclient


@pytest.fixture()
def connection() -> Connection:
    engine = create_engine(os.environ["DB_DSN"])
    yield engine.connect()
    engine.dispose()


@pytest.fixture(scope='function')
def authorized_headers(client: FlaskClient) -> Dict:
    user_dto = CreatingUserRequestFactory.build()
    response = client.post("/user/register", json=user_dto.__dict__)

    assert 'access_token' in response.json
    access_token = response.json['access_token']
    headers = {
        'Authorization': 'Bearer {}'.format(access_token)
    }

    yield headers
