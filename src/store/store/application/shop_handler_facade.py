#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Union

import injector
from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert

from foundation.domain_events.identity_events import UserCreatedEvent
from foundation.domain_events.inventory_events import WarehouseCreatedEvent
from foundation.events import EveryModuleMustCatchThisEvent
from foundation.logger import logger
from store.adapter.queries.query_factories import get_product_query_factory, list_product_collections_query_factory, \
    get_suppliers_bound_to_product_query
from store.adapter.shop_db import shop_catalog_table, \
    shop_collection_table, shop_product_data_cache_table
from store.application.queries.dtos.store_catalog_dto import _row_to_catalog_dto
from store.application.queries.dtos.store_collection_dto import _row_to_collection_dto
from store.application.queries.dtos.store_product_brand_dto import _row_to_brand_dto
from store.application.queries.dtos.store_supplier_dto import _row_to_supplier_dto
from store.application.services.store_unit_of_work import ShopUnitOfWork
from store.domain.entities.registration_status import RegistrationStatus
from store.domain.entities.value_objects import ShopCatalogId, ShopProductId, ShopStatus
from store.domain.events.store_catalog_events import StoreCatalogDeletedEvent
from store.domain.events.store_product_events import StoreProductCreatedEvent, StoreProductUpdatedEvent


class ShopHandlerFacade:
    def __init__(self, uow: ShopUnitOfWork):
        self._uow = uow
        self._conn = None

    # def update_store_catalog_cache(self, store_id: StoreId, catalog_id: StoreCatalogId, catalog_reference: str):
    #     query = insert(store_catalog_cache_table).values(**{
    #         'store_id': store_id,
    #         'catalog_id': catalog_id,
    #         'catalog_reference': catalog_reference
    #     })
    #
    #     self._conn.execute(query)
    #
    # def update_store_collection_cache(self, store_id: StoreId, catalog_id: StoreCatalogId,
    #                                   collection_id: StoreCollectionId, collection_reference: str):
    #     query = insert(store_collection_cache_table).values(**{
    #         'store_id': store_id,
    #         'catalog_id': catalog_id,
    #         'collection_id': collection_id,
    #         'collection_reference': collection_reference
    #     })
    #
    #     self._conn.execute(query)

    def update_store_cache(self, store_id):
        # just to do something with the cache
        pass

    def delete_orphan_catalog_children(self, catalog_id: ShopCatalogId):
        query = delete(shop_catalog_table).where(shop_catalog_table.c.catalog_id == catalog_id)
        self._conn.execute(query)

        query = delete(shop_collection_table).where(shop_collection_table.c.catalog_id is None)
        self._conn.execute(query)

    def update_store_product_cache(self, product_id: ShopProductId, is_updated=False, updated_keys=[]):
        """
        Update the product info into cache

        :param product_id: id of the updated product
        """
        try:
            query = get_product_query_factory(product_id=product_id)
            product_data = self._conn.execute(query).first()

            if not product_data:
                return

            # get catalog and brand
            catalog_json = _row_to_catalog_dto(product_data, collections=[])
            brand_json = _row_to_brand_dto(product_data)

            # get collections
            query = list_product_collections_query_factory(product_id=product_id)
            collections_data = self._conn.execute(query).all()
            collections_json = [_row_to_collection_dto(r) for r in collections_data]

            # get suppliers
            query = get_suppliers_bound_to_product_query(product_id=product_id)
            suppliers_data = self._conn.execute(query).all()
            suppliers_json = [_row_to_supplier_dto(r) for r in suppliers_data]

            # insert data
            data = {
                'product_cache_id': product_id,
                'store_id': product_data.shop_id,
                'catalog_id': product_data.catalog_id,
                'brand_id': product_data.brand_id,
                'catalog_json': catalog_json,
                'collections_json': collections_json,
                'brand_json': brand_json,
                'suppliers_json': suppliers_json,
            }
            stmt = insert(shop_product_data_cache_table).values(**data)

            # or update if duplicated
            on_duplicate_key_stmt = stmt.on_conflict_do_update(
                constraint=shop_product_data_cache_table.primary_key,
                set_=data
            )

            self._conn.execute(on_duplicate_key_stmt)
        except Exception as exc:
            logger.exception(exc)

    def update_shop_registration(self, user_id: str, email: str, mobile: str,
                                 user_created_at: datetime) -> None:
        with self._uow as uow:  # type:ShopUnitOfWork
            try:
                registration = uow.shops.get_registration_by_email(email=email)  # type:'ShopRegistration'
                logger.info(f'Registration found {registration.registration_id}')

                # return None if nothing found
                if not registration:
                    return

                # if registration.status == RegistrationStatus.REGISTRATION_CONFIRMED_YET_COMPLETED and registration.last_updated < user_created_at:
                if registration:
                    shop_user = registration.generate_shop_admin(user_id=user_id, email=email, mobile=mobile)
                    shop = registration.create_shop(shop_admin=shop_user)

                    uow.shops.save(shop)

                    # update registration
                    registration.status = RegistrationStatus.REGISTRATION_CONFIRMED_COMPLETED
                    uow.commit()
            except Exception as exc:
                raise exc

    def update_shop_status(self, warehouse_id: str, warehouse_name: str, admin_id: str,
                           warehouse_created_at: datetime,
                           new_shop_status: ShopStatus):
        with self._uow as uow:  # type:ShopUnitOfWork
            try:
                shop = uow.shops.get_shop_by_admin_id(user_id=admin_id)  # type:'Shop'
                if not shop:
                    return

                if shop.status == ShopStatus.WAREHOUSE_YET_CREATED and shop.last_updated < warehouse_created_at:
                    shop.status = ShopStatus.NORMAL
                    shop.add_warehouse(warehouse_id=warehouse_id, warehouse_name=warehouse_name)

                uow.commit()
            except Exception as exc:
                raise exc


# class StoreCatalogCreatedEventHandler:
#     @injector.inject
#     def __init__(self, facade: StoreHandlerFacade):
#         self._facade = facade
#
#     def __call__(self, event: StoreCatalogCreatedEvent) -> None:
#         self._facade.update_store_catalog_cache(event.shop_id, event.catalog_id, event.catalog_reference)


class StoreCatalogDeletedEventHandler:
    @injector.inject
    def __init__(self, facade: ShopHandlerFacade):
        self._facade = facade

    def __call__(self, event: StoreCatalogDeletedEvent) -> None:
        self._facade.delete_orphan_catalog_children(event.catalog_id)
        # self._facade.update_store_catalog_cache(event.shop_id)


# class StoreCollectionCreatedEventHandler:
#     @injector.inject
#     def __init__(self, facade: StoreHandlerFacade):
#         self._facade = facade
#
#     def __call__(self, event: StoreCollectionCreatedEvent) -> None:
#         self._facade.update_store_collection_cache(
#             event.shop_id,
#             event.catalog_id,
#             event.collection_id,
#             event.collection_reference
#         )

class StoreProductCreatedOrUpdatedEventHandler:
    @injector.inject
    def __init__(self, facade: ShopHandlerFacade):
        self._facade = facade

    def __call__(self, event: Union[StoreProductCreatedEvent, StoreProductUpdatedEvent]) -> None:
        if isinstance(event, StoreProductCreatedEvent):
            self._facade.update_store_product_cache(event.product_id)
        elif isinstance(event, StoreProductUpdatedEvent):
            self._facade.update_store_product_cache(event.product_id, is_updated=True, updated_keys=event.updated_keys)


class UpdateShopWhileWarehouseCreatedEventHandler:
    @injector.inject
    def __init__(self, facade: ShopHandlerFacade):
        self._f = facade

    def __call__(self, event: WarehouseCreatedEvent):
        try:
            self._f.update_shop_status(
                warehouse_id=event.warehouse_id,
                admin_id=event.admin_id,
                warehouse_name=event.warehouse_name,
                warehouse_created_at=event.warehouse_created_at,
                new_shop_status=ShopStatus.NORMAL
            )
        except Exception as exc:
            pass


class CreateShopAndUpdateRegistrationWhileUserCreatedEventHandler:
    @injector.inject
    def __init__(self, facade: ShopHandlerFacade) -> None:
        self._facade = facade

    # def __call__(self, event: UserCreatedEvent) -> None:
    def __call__(self, event: UserCreatedEvent) -> None:
        try:
            event_id = event.event_id
            user_id = event.user_id
            email = event.email
            mobile = event.mobile
            created_at = event.created_at

            # update registration
            self._facade.update_shop_registration(
                user_id=user_id,
                email=email,
                mobile=mobile,
                user_created_at=created_at
            )
        except Exception as exc:
            # do something with this exception
            logger.exception(exc)
            raise exc
