#!/usr/bin/env python
# -*- coding: utf-8 -*-

import injector
from sqlalchemy import update, and_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Connection

from foundation.events import EventBus, new_event_id
from foundation.logger import logger
from identity.domain.events import UnexistentUserRequestEvent
from identity.domain.value_objects import UserId
from shop.adapter.id_generators import generate_shop_id, generate_shop_catalog_id
from shop.adapter.queries.query_factories import (
    get_shop_product_query_factory,
    list_suppliers_bound_to_product_query,
    list_shop_collections_bound_to_product_query_factory, list_units_bound_to_product_query_factory,
)
from shop.adapter.shop_db import shop_product_view_cache_table, shop_users_table, shop_table, shop_warehouse_table, \
    shop_catalog_table
from shop.application.services.shop_unit_of_work import ShopUnitOfWork
from shop.domain.dtos.catalog_dtos import _row_to_catalog_dto
from shop.domain.dtos.collection_dtos import _row_to_collection_dto
from shop.domain.dtos.shop_brand_dtos import _row_to_brand_dto
from shop.domain.dtos.product_unit_dtos import _row_to_unit_dto
from shop.domain.dtos.supplier_dtos import _row_to_supplier_dto
from shop.domain.entities.value_objects import ShopId, ShopStatus, GenericShopItemStatus, \
    ShopProductId, SystemUserId, ShopUserType, ShopWarehouseId
from shop.domain.events import PendingShopCreatedEvent


class ShopHandlerFacade:
    def __init__(self, uow: ShopUnitOfWork, conn: Connection, eventbus: EventBus):
        self._uow = uow
        self._conn = conn
        self._event_bus = eventbus

    def create_pending_shop(self, user_id: SystemUserId, name: str,
                            procman_id: str):
        shop_id = generate_shop_id()

        # insert new shop
        insertion = insert(shop_table).values(shop_id=shop_id, name=name,
                                              status=ShopStatus.PENDING_CREATION)
        self._conn.execute(insertion)

        # insert shop_users_table
        insertion = insert(shop_users_table).values(user_id=user_id, shop_id=shop_id,
                                                    shop_role=ShopUserType.ADMIN,
                                                    status=GenericShopItemStatus.PENDING_CREATION)
        self._conn.execute(insertion)

        # emit the new event
        self._event_bus.post(PendingShopCreatedEvent(event_id=new_event_id(),
                                                     procman_id=procman_id,
                                                     shop_id=shop_id))

    def create_shop_default_catalog(self, shop_id: ShopId):
        insertion = insert(shop_catalog_table).values(catalog_id=generate_shop_catalog_id(),
                                                      shop_id=shop_id,
                                                      title='Default Catalog',
                                                      default=True,
                                                      status=GenericShopItemStatus.NORMAL)
        self._conn.execute(insertion)

    def activate_pending_shop(self, shop_id: ShopId, user_id: UserId):
        modification = update(shop_table).values(status=ShopStatus.NORMAL).where(shop_table.c.shop_id == shop_id)
        self._conn.execute(modification)
        modification = update(shop_users_table).values(status=GenericShopItemStatus.NORMAL).where(
            and_(shop_users_table.c.shop_id == shop_id, shop_users_table.c.user_id == user_id))
        self._conn.execute(modification)

    def update_shop_user_data(self, user_id: SystemUserId, email: str, mobile: str):
        modification = update(shop_users_table).where(shop_users_table.c.user_id == user_id).values(email=email,
                                                                                                    mobile=mobile)
        self._conn.execute(modification)

    def add_shop_warehouse(self, shop_id: ShopId, warehouse_id: ShopWarehouseId):
        insertion = insert(shop_warehouse_table).values(shop_id=shop_id, warehouse_id=warehouse_id)
        self._conn.execute(insertion)

    def update_shop_product_cache(self, product_id: ShopProductId, shop_id: ShopId):
        query = get_shop_product_query_factory(product_id=product_id, shop_id=shop_id)
        product_data = self._conn.execute(query).first()

        if not product_data:
            return

        # get catalog and brand
        catalog_json = _row_to_catalog_dto(product_data, collections=[])
        brand_json = _row_to_brand_dto(product_data) if product_data.brand_id else None

        # get collections
        query = list_shop_collections_bound_to_product_query_factory(shop_id=shop_id, product_id=product_id)
        collections_data = self._conn.execute(query).all()
        collections_json = [_row_to_collection_dto(r) for r in collections_data]

        # get suppliers
        query = list_suppliers_bound_to_product_query(shop_id=shop_id, product_id=product_id)
        suppliers_data = self._conn.execute(query).all()
        suppliers_json = [_row_to_supplier_dto(r, []) for r in suppliers_data]

        # get units_json
        query = list_units_bound_to_product_query_factory(shop_id=shop_id, product_id=product_id)
        units_data = self._conn.execute(query).all()
        units_json = [_row_to_unit_dto(r) for r in units_data]

        # insert data
        data = {
            'product_cache_id': product_id,
            'shop_id': product_data.shop_id,
            'catalog_id': product_data.catalog_id,
            'brand_id': product_data.brand_id,
            'catalog_json': catalog_json,
            'collections_json': collections_json,
            'brand_json': brand_json,
            'suppliers_json': suppliers_json,
            'units_json': units_json,
            'status': product_data.status,
        }
        stmt = insert(shop_product_view_cache_table).values(**data)

        # or update if duplicated
        on_duplicate_key_stmt = stmt.on_conflict_do_update(
            constraint=shop_product_view_cache_table.primary_key,
            set_=data
        )

        self._conn.execute(on_duplicate_key_stmt)


# class CreateDefaultCatalogUponShopCreatedHandler:
#     @injector.inject
#     def __init__(self, facade: ShopHandlerFacade):
#         self._f = facade
#
#     def __call__(self, event: ShopCreatedEvent):
#         try:
#             event_id = event.event_id
#             shop_id = event.shop_id
#             self._f.create_shop_default_catalog(shop_id=shop_id)
#         except Exception as exc:
#             pass


class DisableUnexistentSystemUserHandler:
    @injector.inject
    def __init__(self, connection: Connection):
        self._connection = connection

    def __call__(self, event: UnexistentUserRequestEvent):
        try:
            user_id = event.user_id

            # update user
            q = update(shop_users_table).where(shop_users_table.c.user_id == user_id).values(
                status=GenericShopItemStatus.DELETED)
            self._connection.execute(q)
        except Exception as exc:
            logger.exception(exc)
            raise exc
