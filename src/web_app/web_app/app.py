from typing import Optional

from flask import Flask, Response, request
from flask_cors import CORS
from flask_injector import FlaskInjector
from flask_jwt_extended import JWTManager
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Session

from main import bootstrap_app
from main.modules import RequestScope
from web_app.blueprints.auctions import AuctionsWeb, auctions_blueprint
from web_app.blueprints.auth import auth_blueprint, AuthenticationAPI
from web_app.blueprints.catalog import catalog_blueprint, CatalogAPI
from web_app.blueprints.product import product_blueprint, ProductAPI
from web_app.blueprints.shipping import shipping_blueprint
from web_app.json_encoder import JSONEncoder
from web_app.security import setup as security_setup


def create_app(settings_override: Optional[dict] = None) -> Flask:
    if settings_override is None:
        settings_override = {}

    app = Flask(__name__)

    app.json_encoder = JSONEncoder

    app.register_blueprint(auth_blueprint, url_prefix='/user')
    app.register_blueprint(catalog_blueprint, url_prefix='/catalog')
    app.register_blueprint(product_blueprint, url_prefix='/product')
    app.register_blueprint(auctions_blueprint, url_prefix="/auctions")
    app.register_blueprint(shipping_blueprint, url_prefix="/shipping")

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
        ProductAPI()], injector=app_context.injector)
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
    app.config['JWT_BLACKLIST_ENABLED'] = True
    app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
    jwt = JWTManager(app)

    # @jwt.token_in_blacklist_loader
    # def check_if_token_in_blacklist(decrypted_token):
    #     jti = decrypted_token['jti']
    #     return models.RevokedTokenModel.is_jti_blacklisted(jti)

    # enable swagger
    # swagger = Swagger(app)

    # enable CORS
    CORS(app)

    return app
