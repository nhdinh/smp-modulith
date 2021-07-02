import os
from dataclasses import dataclass

import dotenv
import injector
from sqlalchemy.engine import Engine, create_engine

from auctions import Auctions
from auctions_infrastructure import AuctionsInfrastructure
from customer_relationship import CustomerRelationship
from db_infrastructure import metadata
from foundation import FoundationModule
from identity import IdentityModule
from identity.auth_infrastructure_module import AuthenticationInfrastructureModule
from identity.auth_module import AuthenticationModule
from inventory import InventoryModule, InventoryInfrastructureModule
from main.modules import Configs, Db, EventBusMod, RedisMod, Rq, MinIOService, FileSystemProvider
from payments import Payments
from processes import Processes
from product_catalog import ProductCatalogModule, ProductCatalogInfrastructureModule
from shipping import Shipping
from shipping_infrastructure import ShippingInfrastructure
from store import StoreInfrastructureModule, StoreModule

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
        "payments.login": os.environ["PAYMENTS_LOGIN"],
        "payments.password": os.environ["PAYMENTS_PASSWORD"],
        "email.host": os.environ["EMAIL_HOST"],
        "email.port": os.environ["EMAIL_PORT"],
        "email.username": os.environ["EMAIL_USERNAME"],
        "email.password": os.environ["EMAIL_PASSWORD"],
        "email.from.name": os.environ["EMAIL_FROM_NAME"],
        "email.from.address": os.environ["EMAIL_FROM_ADDRESS"],
        "redis.host": os.environ["REDIS_HOST"],
        "minio.host": os.environ["MINIO_HOST"],
        "minio.access_key": os.environ["MINIO_ACCESS_KEY"],
        "minio.secret_key": os.environ["MINIO_SECRET_KEY"],
    }

    db_echo = os.environ.get('DB_ECHO') in ('True', 'true', '1')

    engine = create_engine(os.environ["DB_DSN"], isolation_level="REPEATABLE READ", echo=db_echo)
    dependency_injector = _setup_dependency_injection(settings, engine)
    _setup_orm_events(dependency_injector)

    _create_db_schema(engine)  # TEMPORARY

    _setup_orm_mappings(dependency_injector)

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
            FoundationModule(),
            IdentityModule(),
            AuthenticationInfrastructureModule(),
            AuthenticationModule(),
            Auctions(),
            AuctionsInfrastructure(),
            Shipping(),
            ShippingInfrastructure(),
            CustomerRelationship(),
            ProductCatalogModule(),
            ProductCatalogInfrastructureModule(),
            StoreModule(),
            StoreInfrastructureModule(),
            InventoryModule(),
            InventoryInfrastructureModule(),
            Payments(),
            Processes(),
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
        from store.adapter import store_mappers
        store_mappers.start_mappers()
    except Exception as exc:
        raise exc

    try:
        from inventory.adapter import inventory_mappers
        inventory_mappers.start_mappers()
    except Exception as exc:
        raise exc


def _create_db_schema(engine: Engine) -> None:
    # Models has to be imported for metadata.create_all to discover them
    from product_catalog import catalog_table, product_table  # noqa
    from auctions_infrastructure import auctions, bids  # noqa
    from customer_relationship.models import customers  # noqa
    from identity.adapters.identity_db import user_table, role_table, roles_users_table  # noqa
    from inventory.adapter.inventory_db import draft_purchase_order_table, inventory_product_balance_table  # noqa


    # TODO: Use migrations for that
    metadata.create_all(bind=engine)

    pass
