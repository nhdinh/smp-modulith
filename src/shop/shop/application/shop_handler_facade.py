#!/usr/bin/env python
# -*- coding: utf-8 -*-

import injector
from sqlalchemy import update, and_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Connection

from foundation.events import EventBus, new_event_id, DomainEvent
from foundation.logger import logger
from identity.domain.events import UnexistentUserRequestEvent
from identity.domain.value_objects import UserId
from shop.adapter.id_generators import generate_shop_id, generate_shop_catalog_id
from shop.adapter.shop_db import shop_users_table, shop_table, shop_warehouse_table, \
    shop_catalog_table
from shop.application.services.shop_unit_of_work import ShopUnitOfWork
from shop.domain.entities.value_objects import ShopId, ShopStatus, GenericShopItemStatus, \
    SystemUserId, ShopUserType, ShopWarehouseId
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


class DomainEventConverterHandler:
    @injector.inject
    def __init__(self):
        self.event_types_mapping = {
            'PURCHASE_PRICE_CREATED': None
            # Tại sao tao lại cần phải biết về cái price đã được created? Tao có cần phải quan tâm đến nó hay không vậy nhỉ?
        }

    def __call__(self, event: DomainEvent):
        if event.type in self.event_types_mapping.keys():
            event_type = self.event_types_mapping[event.type]
            if (event_type):
                return event_type(event.payload)

        # nothing matched, return None
        return None
