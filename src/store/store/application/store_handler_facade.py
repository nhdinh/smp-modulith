#!/usr/bin/env python
# -*- coding: utf-8 -*-
from select import select

import injector
from sqlalchemy import insert
from sqlalchemy.engine import Connection
from sqlalchemy.orm import sessionmaker, Session
from store.adapter.store_db import store_table, store_owner_table
from store.domain.entities.value_objects import StoreOwnerId, StoreId


class StoreHandlerFacade:
    def __init__(self, connection: Connection):
        self._conn = connection

    def create_store(
            self,
            store_id: StoreId,
            store_owner: StoreOwnerId,
            store_name: str,
            owner_email: str,
            owner_mobile: str,
            owner_hashed_password: str,
    ) -> None:
        create_owner_query = insert(store_owner_table).values(
            id=store_owner,
            email=owner_email,
            mobile=owner_mobile,
            password=owner_hashed_password,
        )

        create_store_query = insert(store_table).values(
            store_id=store_id,
            name=store_name,
            owner=store_owner,
        )

        try:
            sess = sessionmaker(bind=self._conn)
            sess = sess()  # type:Session
            sess.execute(create_owner_query)
            sess.execute(create_store_query)
            sess.commit()
            sess.close()
        except Exception as exc:
            raise exc


class StoreRegistrationConfirmedEventHandler:
    @injector.inject
    def __init__(self, facade: StoreHandlerFacade):
        self._facade = facade

    def __call__(self, event):
        self._facade.create_store(
            store_id=event.store_id,
            store_name=event.store_name,
            store_owner=event.owner_id,
            owner_email=event.email,
            owner_mobile=event.mobile,
            owner_hashed_password=event.hashed_password
        )
