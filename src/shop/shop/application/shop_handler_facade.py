#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime

import injector

from foundation.domain_events.identity_events import UserCreatedEvent
from foundation.domain_events.inventory_events import WarehouseCreatedEvent
from foundation.events import EveryModuleMustCatchThisEvent
from foundation.logger import logger
from shop.application.services.shop_unit_of_work import ShopUnitOfWork
from shop.domain.entities.value_objects import RegistrationStatus, ShopStatus


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

    def update_shop_registration(self, user_id: str, email: str, mobile: str,
                                 user_created_at: datetime) -> None:
        with self._uow as uow:  # type:ShopUnitOfWork
            try:
                registration = uow.shops.get_registration_by_email(email=email)  # type:'ShopRegistration'

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


class Shop_CatchAllEventHandler:
    @injector.inject
    def __init__(self, facade: ShopHandlerFacade):
        self._f = facade

    def __call__(self, event: EveryModuleMustCatchThisEvent):
        self._f.do_something_with_catchall_event(event)


class CreateShopAndUpdateRegistrationWhileUserCreatedEventHandler:
    @injector.inject
    def __init__(self, facade: ShopHandlerFacade):
        self._facade = facade

    def __call__(self, event: UserCreatedEvent):
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
