from datetime import timedelta, datetime, timezone
from typing import Optional

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask import Flask, Response, request, make_response
from flask_cors import CORS
from flask_injector import FlaskInjector
from flask_jwt_extended import JWTManager, get_jwt, create_access_token, get_jwt_identity, set_access_cookies
from flask_log_request_id import current_request_id, RequestID
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Session

from main import bootstrap_app
from main.modules import RequestScope
from web_app.blueprints.auctions import AuctionsWeb, auctions_blueprint
from web_app.blueprints.auth_bp import auth_blueprint, AuthenticationAPI
from web_app.blueprints.brand import brand_blueprint
from web_app.blueprints.catalog_bp import catalog_blueprint, CatalogAPI
from web_app.blueprints.inventory_bp import inventory_blueprint, InventoryAPI
from web_app.blueprints.product_bp import product_blueprint, ProductAPI
from web_app.blueprints.shipping import shipping_blueprint
from web_app.blueprints.shop_bp import shop_blueprint, ShopAPI
from web_app.blueprints.shop_catalog_bp import ShopCatalogAPI, shop_catalog_blueprint
from web_app.blueprints.store_catalog_bp import store_catalog_blueprint, StoreCatalogAPI, \
    store_catalog_blueprint_endpoint_callers, STORE_CATALOG_BLUEPRINT_NAME
from web_app.blueprints.store_management_bp import store_management_blueprint, StoreAPI
from web_app.json_encoder import JSONEncoder
from web_app.openapi import docs


def create_app(settings_override: Optional[dict] = None) -> Flask:
    if settings_override is None:
        settings_override = {}

    app = Flask(__name__)

    app.json_encoder = JSONEncoder
    app.url_map.strict_slashes = False

    # config openapi
    app.config.update({
        'APISPEC_SPEC': APISpec(title='SMP', openapi_version='3.0', version='v1', plugins=[MarshmallowPlugin()]),
        'APISPEC_SWAGGER_URL': '/docs',
    })
    # docs.init_app(app)

    # register all blueprints
    app.register_blueprint(auth_blueprint, url_prefix='/user')
    app.register_blueprint(catalog_blueprint, url_prefix='/catalog')
    app.register_blueprint(product_blueprint, url_prefix='/product')
    app.register_blueprint(auctions_blueprint, url_prefix="/auctions")
    app.register_blueprint(shipping_blueprint, url_prefix="/shipping")
    app.register_blueprint(brand_blueprint, url_prefix='/brand')
    app.register_blueprint(store_management_blueprint, url_prefix='/manage-store')

    app.register_blueprint(shop_blueprint, url_prefix='/shop')
    app.register_blueprint(shop_catalog_blueprint, url_prefix='/shop_catalog')
    app.register_blueprint(store_catalog_blueprint, url_prefix='/store-catalog')
    app.register_blueprint(inventory_blueprint, url_prefix='/inventory')
    for _handler in store_catalog_blueprint_endpoint_callers:
        docs.register(_handler, blueprint=STORE_CATALOG_BLUEPRINT_NAME)

    # TODO: move this config
    app.config["SECRET_KEY"] = "super-secret"
    app.config["DEBUG"] = True
    app.config["SECURITY_SEND_REGISTER_EMAIL"] = False
    app.config["SECURITY_REGISTERABLE"] = True
    app.config["SECURITY_PASSWORD_SALT"] = "99f885320c0f867cde17876a7849904c41a2b8120a9a9e76d1789e458e543af9"
    app.config["WTF_CSRF_ENABLED"] = False
    for key, value in settings_override.items():
        app.config[key] = value

    app_context = bootstrap_app()
    FlaskInjector(app, modules=[
        AuthenticationAPI(),
        AuctionsWeb(),
        CatalogAPI(),
        ProductAPI(),
        StoreAPI(),

        ShopAPI(),
        ShopCatalogAPI(),

        StoreCatalogAPI(),
        InventoryAPI(),
    ], injector=app_context.injector)
    app.injector = app_context.injector

    @app.before_request
    def transaction_start() -> None:
        app_context.injector.get(RequestScope).enter()

        request.connection = app_context.injector.get(Connection)  # type: ignore
        request.tx = request.connection.begin()  # type: ignore
        request.session = app_context.injector.get(Session)  # type: ignore

    @app.after_request
    def transaction_commit(response: Response) -> Response:
        scope = app_context.injector.get(RequestScope)
        try:
            if hasattr(request, "tx") and response.status_code < 400:
                request.tx.commit()  # type: ignore
        finally:
            scope.exit()

        return response

    @app.after_request
    def add_cors_headers(response: Response) -> Response:
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response

    # has to be done after DB-hooks, because it relies on DB
    # security_setup(app)

    # enable jwt
    app.config['JWT_SECRET_KEY'] = app.config['SECRET_KEY']
    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

    if app.debug:
        app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=2)

    jwt = JWTManager()
    jwt.init_app(app)

    app.config['LOG_REQUEST_ID_GENERATE_IF_NOT_FOUND'] = True
    app.config['LOG_REQUEST_ID_LOG_ALL_REQUESTS'] = True
    app.config['LOG_REQUEST_ID_G_OBJECT_ATTRIBUTE'] = 'current_request_id'
    RequestID(app)

    @app.after_request
    def refresh_expiring_jwts(response):
        try:
            exp_timestamp = get_jwt()["exp"]
            now = datetime.now(timezone.utc)
            target_timestamp = datetime.timestamp(now + timedelta(minutes=30))

            if target_timestamp > exp_timestamp:
                access_token = create_access_token(identity=get_jwt_identity())
                set_access_cookies(response, access_token)
            return response
        except (RuntimeError, KeyError):
            # Case where there is not a valid JWT. Just return the original response
            return response

    @app.after_request
    def append_request_id(response):
        response.headers.add('X-REQUEST-ID', current_request_id())

        return response

    # enable CORS
    CORS(app)

    @app.route('/health/live')
    def health_check():
        return make_response({'status': True}), 200

    return app
