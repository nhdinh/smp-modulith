#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime

import injector
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Connection

from foundation.domain_events.identity_events import ShopAdminCreatedEvent
from foundation.domain_events.inventory_events import WarehouseCreatedEvent
from foundation.domain_events.shop_events import ShopCreatedEvent, ShopProductCreatedEvent
from foundation.events import EveryModuleMustCatchThisEvent
from foundation.logger import logger
from shop.adapter.queries.query_factories import (
    get_shop_product_query_factory,
    list_suppliers_bound_to_product_query,
    list_shop_collections_bound_to_product_query_factory,
)
from shop.adapter.shop_db import shop_product_view_cache_table
from shop.application.services.shop_unit_of_work import ShopUnitOfWork
from shop.domain.dtos.catalog_dtos import _row_to_catalog_dto
from shop.domain.dtos.collection_dtos import _row_to_collection_dto
from shop.domain.dtos.product_brand_dtos import _row_to_brand_dto
from shop.domain.dtos.supplier_dtos import _row_to_supplier_dto
from shop.domain.entities.shop import Shop
from shop.domain.entities.value_objects import RegistrationStatus, ShopId, ShopStatus


class ShopHandlerFacade:
    def __init__(self, uow: ShopUnitOfWork):
        self._uow = uow

    def do_something_with_catchall_event(self, event: EveryModuleMustCatchThisEvent):
        with self._uow as uow:  # type:ShopUnitOfWork
            try:
                uow.commit()
            except Exception as exc:
                logger.exception(exc)
                raise exc

    def create_shop_upon_confirmation(self, user_id: str, email: str, mobile: str,
                                      user_created_at: datetime) -> None:
        with self._uow as uow:  # type:ShopUnitOfWork
            try:
                registration = uow.shops.get_registration_by_email(email=email)  # type:'ShopRegistration'

                # return None if nothing found
                if not registration:
                    return

                # if valid registration
                if registration.status == RegistrationStatus.REGISTRATION_CONFIRMED_YET_COMPLETED and registration.last_updated < user_created_at:
                    # check if shop is created or not
                    shop = uow.shops.get_shop_by_admin_id(user_id=user_id)

                    # shop has been created, log the suspected action
                    if shop:
                        logger.debug(
                            f'Shop and ShopAdmin both created but ShopAdminCreatedEvent emitted. ShopId={shop.shop_id}. AdminId={user_id}')
                        return

                    # else, created
                    shop_user = registration.generate_shop_admin(user_id=user_id, email=email, mobile=mobile)
                    shop = registration.create_shop(shop_admin=shop_user)

                    uow.shops.save(shop)

                    # update registration
                    registration.status = RegistrationStatus.REGISTRATION_CONFIRMED_COMPLETED
                    uow.commit()
            except Exception as exc:
                raise exc

    def update_shop_warehouse_list(self, admin_id: str, new_warehouse_id: str, warehouse_name: str,
                                   warehouse_created_at: datetime):
        with self._uow as uow:  # type: ShopUnitOfWork
            try:
                shop = uow.shops.get_shop_by_admin_id(user_id=admin_id)  # type:Shop
                if not shop:
                    return

                # add brand new warehouse to shop
                if shop and shop.status == ShopStatus.WAREHOUSE_YET_CREATED and shop.last_updated < warehouse_created_at:
                    shop.status = ShopStatus.NORMAL
                    shop.add_warehouse(warehouse_id=new_warehouse_id, warehouse_name=warehouse_name)

                uow.commit()
            except Exception as exc:
                raise exc

    def create_shop_default_catalog(self, shop_id: ShopId):
        with self._uow as uow:  # type:ShopUnitOfWork
            try:
                shop = uow.shops.get(shop_id_to_find=shop_id)  # type:Shop
                if shop:
                    shop.create_default_catalog()
            except Exception as exc:
                raise exc


class Shop_CatchAllEventHandler:
    @injector.inject
    def __init__(self, facade: ShopHandlerFacade):
        self._f = facade

    def __call__(self, event: EveryModuleMustCatchThisEvent):
        self._f.do_something_with_catchall_event(event)


class CreateShopAndUpdateRegistrationUponUserCreatedHandler:
    @injector.inject
    def __init__(self, facade: ShopHandlerFacade):
        self._facade = facade

    def __call__(self, event: ShopAdminCreatedEvent):
        try:
            event_id = event.event_id
            user_id = event.user_id
            email = event.email
            mobile = event.mobile
            created_at = event.created_at

            # update registration
            self._facade.create_shop_upon_confirmation(
                user_id=user_id,
                email=email,
                mobile=mobile,
                user_created_at=created_at
            )
        except Exception as exc:
            logger.exception(exc)
            raise exc


class AddWarehouseToShopUponWarehouseCreatedHandler:
    @injector.inject
    def __init__(self, facade: ShopHandlerFacade):
        self._facade = facade = facade

    def __call__(self, event: WarehouseCreatedEvent):
        try:
            event_id = event.event_id
            warehouse_user_id = event.admin_id
            warehouse_id = event.warehouse_id
            warehouse_name = event.warehouse_name
            warehouse_created_at = event.warehouse_created_at

            self._facade.update_shop_warehouse_list(
                admin_id=warehouse_user_id, new_warehouse_id=warehouse_id,
                warehouse_name=warehouse_name,
                warehouse_created_at=warehouse_created_at
            )
        except Exception as exc:
            logger.exception(exc)
            raise exc


class CreateDefaultCatalogUponShopCreatedHandler:
    @injector.inject
    def __init__(self, facade: ShopHandlerFacade):
        self._f = facade

    def __call__(self, event: ShopCreatedEvent):
        try:
            event_id = event.event_id
            shop_id = event.shop_id
            self._f.create_shop_default_catalog(shop_id=shop_id)
        except Exception as exc:
            pass


class GenerateViewCacheUponProductModificationHandler:
    @injector.inject
    def __init__(self, facade: ShopHandlerFacade, connection: Connection):
        self._facade = facade
        self._c = connection

    def __call__(self, event: ShopProductCreatedEvent):
        pass
        try:
            event_id = event.event_id
            product_id = event.product_id
            current_connection = self._c

            query = get_shop_product_query_factory(product_id=product_id)
            product_data = current_connection.execute(query).first()

            if not product_data:
                return

            # get catalog and brand
            catalog_json = _row_to_catalog_dto(product_data, collections=[])
            brand_json = _row_to_brand_dto(product_data) if product_data.brand_id else None

            # get collections
            query = list_shop_collections_bound_to_product_query_factory(product_id=product_id)
            collections_data = current_connection.execute(query).all()
            collections_json = [_row_to_collection_dto(r) for r in collections_data]

            # get suppliers
            query = list_suppliers_bound_to_product_query(product_id=product_id)
            suppliers_data = current_connection.execute(query).all()
            suppliers_json = [_row_to_supplier_dto(r) for r in suppliers_data]

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
            }
            stmt = insert(shop_product_view_cache_table).values(**data)

            # or update if duplicated
            on_duplicate_key_stmt = stmt.on_conflict_do_update(
                constraint=shop_product_view_cache_table.primary_key,
                set_=data
            )

            current_connection.execute(on_duplicate_key_stmt)
        except Exception as exc:
            logger.exception(exc)
            raise exc
