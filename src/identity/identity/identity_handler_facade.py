#!/usr/bin/env python
# -*- coding: utf-8 -*-

import injector
from sqlalchemy import insert, update, select
from sqlalchemy.engine import Connection

from foundation.events import EveryModuleMustCatchThisEvent, new_event_id, EventBus
from identity.adapters.id_generator import generate_user_id
from identity.adapters.identity_db import user_table, user_role_table, role_table
from identity.domain.entities.role import SystemRoleEnum
from identity.domain.entities.user import UserStatus
from identity.domain.events import PendingUserCreatedEvent, UserDataEmitEvent
from identity.domain.value_objects import UserId


class IdentityHandlerFacade:
    def __init__(self, conn: Connection, event_bus: EventBus):
        self._conn = conn
        self._event_bus = event_bus

    def create_pending_user(self, email: str, mobile: str, password: str, registration_type: str,
                            registration_id: str, procman_id: str) -> UserId:
        user_id = generate_user_id()
        insertion = insert(user_table).values(
            user_id=user_id,
            email=email,
            mobile=mobile,
            password=password,
            status=UserStatus.PENDING_CREATION,
        )

        self._conn.execute(insertion)

        if registration_type == 'SHOP':
            self._event_bus.post(PendingUserCreatedEvent(event_id=new_event_id(),
                                                         procman_id=procman_id,
                                                         shop_registration_id=registration_id,
                                                         user_id=user_id))
        else:
            # other registration
            pass

    def activate_pending_user(self, user_id: UserId, email: str, mobile: str, procman_id: str):
        # modify user data record
        modification = update(user_table).values(status=UserStatus.NORMAL).where(user_table.c.user_id == user_id)
        self._conn.execute(modification)

        sysuser_role_id = self._conn.scalar(select(role_table).where(role_table.c.name == SystemRoleEnum.SystemUser))

        # add default role
        insert_role = insert(user_role_table).values(user_id=user_id, role_id=sysuser_role_id)
        self._conn.execute(insert_role)

        self._event_bus.post(UserDataEmitEvent(
            event_id=new_event_id(),
            procman_id=procman_id,
            user_id=user_id,
            email=email,
            mobile=mobile
        ))


class Identity_CatchAllEventHandler:
    @injector.inject
    def __init__(self, facade: IdentityHandlerFacade):
        self._f = facade

    def __call__(self, event: EveryModuleMustCatchThisEvent):
        ...
