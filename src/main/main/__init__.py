import os
from dataclasses import dataclass
# from auctions import Auctions
# from auctions_infrastructure import AuctionsInfrastructure
from typing import Dict

import dotenv
import injector
import sentry_sdk
from sqlalchemy.engine import Engine, create_engine

from customer_relationship import CustomerRelationshipEventHandlerModule
from db_infrastructure import metadata
from foundation.foundation_applications_module import FoundationApplicationModule
from foundation.foundation_event_handler_module import FoundationEventHandlerModule
from identity.identity_applications_module import IdentityApplicationModule
from identity.identity_event_handler_module import IdentityEventHandlerModule
from identity.identity_infrastructure_module import IdentityInfrastructureModule
# from inventory.inventory_application_module import InventoryApplicationModule
# from inventory.inventory_event_handler_module import InventoryEventHandlerModule
# from inventory.inventory_infrastructure_module import InventoryInfrastructureModule
from inventory.inventory_application_module import InventoryApplicationModule
from inventory.inventory_event_handler_module import InventoryEventHandlerModule
from inventory.inventory_infrastructure_module import InventoryInfrastructureModule
from main.modules import Configs, Db, EventBusMod, FileSystemProvider, MinIOService, RedisMod, Rq
# from payments import Payments
from processes import Processes
from product_catalog import ProductCatalogInfrastructureModule, ProductCatalogModule
from shop.shop_application_module import ShopApplicationModule
from shop.shop_event_handler_module import ShopEventHandlerModule
from shop.shop_infrastructure_module import ShopInfrastructureModule

# from shipping import Shipping
# from shipping_infrastructure import ShippingInfrastructure


__all__ = ["bootstrap_app"]


@dataclass
class AppContext:
    injector: injector.Injector


def bootstrap_app() -> AppContext:
    """This is bootstrap function independent from the context.

    This should be used for Web, CLI, or worker context."""
    config_path = os.environ.get(
        "CONFIG_PATH", os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, ".env_file")
    )
    dotenv.load_dotenv(config_path)
    settings = {
        'payments.login': os.environ['PAYMENTS_LOGIN'],
        'payments.password': os.environ['PAYMENTS_PASSWORD'],
        'email.host': os.environ['EMAIL_HOST'],
        'email.port': os.environ['EMAIL_PORT'],
        'email.username': os.environ['EMAIL_USERNAME'],
        'email.password': os.environ['EMAIL_PASSWORD'],
        'email.from.name': os.environ['EMAIL_FROM_NAME'],
        'email.from.address': os.environ['EMAIL_FROM_ADDRESS'],
        'redis.host': os.environ['REDIS_HOST'],
        'minio.host': os.environ['MINIO_HOST'],
        'minio.access_key': os.environ['MINIO_ACCESS_KEY'],
        'minio.secret_key': os.environ['MINIO_SECRET_KEY'],
        'sentry_dsn': os.environ['SENTRY_DSN'],
        'debug': os.environ['DEBUG'],
        'db_echo': os.environ.get('DB_ECHO') in ('True', 'true', '1'),

        # first data
        'admin_id': os.environ.get('admin_id') or 'User_00000000000000000000.FiRsT',
        'sysadmin_role': os.environ.get('sysadmin_role') or 'Role_00000000000000000000.FiRsT',
        'sysuser_role': os.environ.get('sysuser_role') or 'Role_00000000000000000000.sEcOn',
        'central_db_repo': os.environ.get('central_db_repo') or 'Shop_00000000000000000000.FiRsT',
        'default_repo_cat': os.environ.get('default_repo_cat') or 'Cat_00000000000000000000.FiRsT',
        'admin_email': os.environ.get('admin_email') or 'admin@smp.io',
        'admin_password': os.environ.get('admin_password') or 'aDmIn_P@55w0rd'
    }

    # init sentry
    sentry_sdk.init(
        settings['sentry_dsn'],

        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0,
    )

    engine = create_engine(os.environ["DB_DSN"], echo=settings['db_echo'])
    dependency_injector = _setup_dependency_injection(settings, engine)
    _setup_orm_events(dependency_injector)

    _setup_orm_mappings(dependency_injector)

    if settings['debug']:
        _create_db_schema(engine=engine, settings=settings)  # TEMPORARY

    return AppContext(dependency_injector)


def _setup_dependency_injection(settings: dict, engine: Engine) -> injector.Injector:
    return injector.Injector(
        [
            Db(engine),
            RedisMod(settings["redis.host"]),
            Rq(),
            EventBusMod(),
            MinIOService(settings["minio.host"], settings["minio.access_key"], settings["minio.secret_key"]),
            FileSystemProvider(),
            Configs(settings),
            Processes(),

            FoundationEventHandlerModule(),
            FoundationApplicationModule(),

            IdentityEventHandlerModule(),
            IdentityInfrastructureModule(),
            IdentityApplicationModule(),

            CustomerRelationshipEventHandlerModule(),
            ProductCatalogModule(),
            ProductCatalogInfrastructureModule(),

            ShopEventHandlerModule(),
            ShopInfrastructureModule(),
            ShopApplicationModule(),

            InventoryEventHandlerModule(),
            InventoryInfrastructureModule(),
            InventoryApplicationModule(),
        ],
        auto_bind=False,
    )


def _setup_orm_events(dependency_injector: injector.Injector) -> None:
    # @sa_event.listens_for(User, "after_insert")
    # def insert_cb(_mapper, _connection: Connection, user: User) -> None:  # type: ignore
    #     dependency_injector.get(CustomerRelationshipFacade).create_customer(user.id, user.email)
    #
    # @sa_event.listens_for(User, "after_update")
    # def update_cb(_mapper, _connection: Connection, user: User) -> None:  # type: ignore
    #     dependency_injector.get(CustomerRelationshipFacade).update_customer(user.id, user.email)
    pass


def _setup_orm_mappings(dependency_injector: injector.Injector) -> None:
    # TODO: do something here to map the data table to model class
    try:
        import foundation.database_setup as foundation_database_setup
        foundation_database_setup.start_mappers()
    except Exception as exc:
        raise exc

    try:
        from identity.adapters import identity_db
        identity_db.start_mappers()
    except Exception as exc:
        raise exc

    try:
        from product_catalog.adapter import catalog_db
        catalog_db.start_mappers()
    except Exception as exc:
        raise exc

    try:
        from shop.adapter import shop_mappers
        shop_mappers.start_mappers()
    except Exception as exc:
        raise exc

    try:
        from inventory.adapter import inventory_mappers
        inventory_mappers.start_mappers()
    except Exception as exc:
        raise exc


def _create_db_schema(settings: Dict, engine: Engine) -> None:
    # TODO: Use migrations for that
    metadata.create_all(bind=engine)

    try:
        from identity.adapters import identity_db
        identity_db.install_first_data(
            engine=engine,
            admin_id=settings['admin_id'],
            sysadmin_role_id=settings['sysadmin_role'],
            sysuser_role_id=settings['sysuser_role'],
            admin_email=settings['admin_email'],
            admin_password=settings['admin_password']
        )

        from shop.adapter import shop_mappers
        shop_mappers.install_first_data(
            engine=engine,
            admin_id=settings['admin_id'],
            admin_email=settings['admin_email'],
            central_db_repo=settings['central_db_repo'],
            default_repo_cat=settings['default_repo_cat'],
        )
    except Exception as exc:
        raise exc
