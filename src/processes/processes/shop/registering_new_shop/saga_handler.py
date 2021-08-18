#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector

from foundation import Event
from foundation.locks import LockFactory
from foundation.method_dispatch import method_dispatch
from identity.domain.events import PendingUserCreatedEvent
from inventory.domain.events import PendingWarehouseCreatedEvent
from processes.repository import new_process_id, ProcessManagerDataRepo
from processes.shop.registering_new_shop.saga import RegisteringNewShop, ShopRegistrationData
from shop.domain.events import ShopRegistrationCreatedEvent, PendingShopCreatedEvent, ShopRegistrationConfirmedEvent


class RegisteringNewShopHandler:
    LOCK_TIMEOUT = 30

    @injector.inject
    def __init__(self, procman: RegisteringNewShop, repo: ProcessManagerDataRepo, lock_factory: LockFactory):
        self._procman = procman
        self._repo = repo
        self._lock_factory = lock_factory

    @method_dispatch
    def __call__(self, event: Event) -> None:
        raise NotImplementedError

    @__call__.register(ShopRegistrationCreatedEvent)  # type:ignore
    def handle_start(self, event: ShopRegistrationCreatedEvent) -> None:
        data = ShopRegistrationData(process_id=new_process_id())
        lock_name = f"pm-lock-{event.registration_id}"
        self._run_process_manager(lock_name, data, event)

    @__call__.register(PendingUserCreatedEvent)  # type:ignore
    def handle_creating_pending_shop(self, event: PendingUserCreatedEvent) -> None:
        data = self._repo.get(event.procman_id, ShopRegistrationData)
        lock_name = f"pm-lock-{data.registration_id}-{event.user_id}"
        self._run_process_manager(lock_name, data, event)

    @__call__.register(PendingShopCreatedEvent)  # type:ignore
    def handle_creating_pending_warehouse(self, event: PendingShopCreatedEvent):
        data = self._repo.get(event.procman_id, ShopRegistrationData)
        lock_name = f"pm-lock-{data.registration_id}-{event.shop_id}"
        self._run_process_manager(lock_name, data, event)

    @__call__.register(PendingWarehouseCreatedEvent)  # type:ignore
    def handle_creating_pending_warehouse(self, event: PendingWarehouseCreatedEvent):
        data = self._repo.get(event.procman_id, ShopRegistrationData)
        lock_name = f"pm-lock-{data.registration_id}-{event.warehouse_id}"
        self._run_process_manager(lock_name, data, event)

    @__call__.register(ShopRegistrationConfirmedEvent)  # type:ignore
    def handle_confirming_shop_registration(self, event: ShopRegistrationConfirmedEvent):
        data = self._repo.get_by_tag(event.registration_id, ShopRegistrationData)
        lock_name = f"pm-lock-{data.registration_id}-confirmation"
        self._run_process_manager(lock_name, data, event)

    def _run_process_manager(self, lock_name: str, data: ShopRegistrationData, event: Event) -> None:
        lock = self._lock_factory(lock_name, self.LOCK_TIMEOUT)

        with lock:
            self._procman.handle(event, data)
            self._repo.save(data.process_id, data)
