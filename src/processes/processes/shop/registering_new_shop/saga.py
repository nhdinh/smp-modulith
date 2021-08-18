#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

from customer_relationship import CustomerRelationshipFacade
from foundation.method_dispatch import method_dispatch
from identity.domain.events import PendingUserCreatedEvent
from identity.identity_handler_facade import IdentityHandlerFacade
from inventory.domain.events import PendingWarehouseCreatedEvent
from inventory.inventory_handler_facade import InventoryHandlerFacade
from processes.value_objects import ProcessId
from shop.application.shop_handler_facade import ShopHandlerFacade
from shop.domain.events import ShopRegistrationCreatedEvent, PendingShopCreatedEvent, ShopRegistrationConfirmedEvent


class State(Enum):
    PROCESS_STARTED = 'PROCESS_STARTED'
    PENDING_USER_CREATED = 'PENDING_USER_CREATED'
    PENDING_SHOP_CREATED = 'PENDING_SHOP_CREATED'  # Shop and Warehouse created. Waiting for confirmation
    WAITING_FOR_CONFIRMATION = 'WAITING_FOR_CONFIRMATION'
    TIMED_OUT = "TIMED_OUT"
    FINISHED = "FINISHED"


@dataclass
class ShopRegistrationData:
    process_id: ProcessId
    state: Optional[State] = None
    timeout_at: Optional[datetime] = None
    tag_id: str = None

    registration_id: Optional[str] = None
    user_id: Optional[str] = None
    shop_id: Optional[str] = None
    warehouse_id: Optional[str] = None
    name: Optional[str] = None
    owner_email: Optional[str] = None
    owner_mobile: Optional[str] = None
    confirmation_token: Optional[str] = None


class RegisteringNewShop:
    def __init__(self,
                 identity_facade: IdentityHandlerFacade,
                 shop_facade: ShopHandlerFacade,
                 inventory_facade: InventoryHandlerFacade,
                 crm_facade: CustomerRelationshipFacade):
        self._identity = identity_facade
        self._shop = shop_facade
        self._inventory = inventory_facade
        self._crm_facade = crm_facade

    def timeout(self, data: ShopRegistrationData):
        assert data.state != State.TIMED_OUT and data.state != State.FINISHED

        data.state = State.TIMED_OUT

    @method_dispatch
    def handle(self, event: Any, data: ShopRegistrationData):
        raise Exception(f"Unhandled event {event}")

    @handle.register(ShopRegistrationCreatedEvent)  # type:ignore
    def handle_creating_shop_registration(self, event: ShopRegistrationCreatedEvent,
                                          data: ShopRegistrationData) -> None:
        assert data.state is None

        self._identity.create_pending_user(email=event.owner_email,
                                           mobile=event.owner_mobile,
                                           password=event.password,
                                           registration_id=event.registration_id,
                                           registration_type='SHOP',
                                           procman_id=data.process_id)

        data.state = State.PENDING_USER_CREATED
        data.tag_id = event.registration_id
        data.registration_id = event.registration_id
        data.name = event.shop_name
        data.owner_email = event.owner_email
        data.owner_mobile = event.owner_mobile
        data.confirmation_token = event.confirmation_token
        data.timeout_at = datetime.now() + timedelta(days=10)

    @handle.register(PendingUserCreatedEvent)  # type:ignore
    def handling_creating_pending_shop(self, event: PendingUserCreatedEvent, data: ShopRegistrationData):
        assert data.state is State.PENDING_USER_CREATED

        self._shop.create_pending_shop(user_id=event.user_id, name=data.name,
                                       procman_id=data.process_id)
        self._inventory.create_pending_warehouse(user_id=event.user_id, warehouse_name=data.name,
                                                 procman_id=data.process_id)
        self._crm_facade.send_store_registration_confirmation_token_email(shop_name=data.name,
                                                                          confirmation_token=data.confirmation_token,
                                                                          owner_email=data.owner_email)
        data.state = State.PENDING_SHOP_CREATED
        data.user_id = event.user_id

    @handle.register(PendingShopCreatedEvent)  # type:ignore
    def handling_pending_shop_created(self, event: PendingShopCreatedEvent, data: ShopRegistrationData):
        assert data.state is State.PENDING_SHOP_CREATED

        self._shop.create_shop_default_catalog(shop_id=event.shop_id)

        data.shop_id = event.shop_id

    @handle.register(PendingWarehouseCreatedEvent)  # type:ignore
    def handing_pending_warehouse_created(self, event: PendingWarehouseCreatedEvent, data: ShopRegistrationData):
        assert data.state is State.PENDING_SHOP_CREATED

        self._shop.add_shop_warehouse(shop_id=data.shop_id, warehouse_id=event.warehouse_id)

        data.warehouse_id = event.warehouse_id
        data.state = State.WAITING_FOR_CONFIRMATION

    @handle.register(ShopRegistrationConfirmedEvent)  # type:ignore
    def handling_confirm_shop_registration(self, event: ShopRegistrationConfirmedEvent, data: ShopRegistrationData):
        assert data.state is State.WAITING_FOR_CONFIRMATION

        self._identity.activate_pending_user(user_id=data.user_id, email=data.owner_email, mobile=data.owner_mobile,
                                             procman_id=data.process_id)
        self._shop.activate_pending_shop(shop_id=data.shop_id, user_id=data.user_id)
        self._inventory.activate_pending_warehouse(warehouse_id=data.warehouse_id, user_id=data.user_id)
        self._crm_facade.send_shop_created_notification_email(shop_name=data.name, email_address=data.owner_email)

        data.state = State.FINISHED
