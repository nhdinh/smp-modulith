#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector
from sqlalchemy.engine import Connection
from sqlalchemy.orm import sessionmaker

from product_catalog.application.usecases.confirm_store_registration import ConfirmingStoreRegistrationResponseBoundary, \
    ConfirmStoreRegistrationUC
from store.adapter import store_db
from store.adapter.sql_store_queries import SqlFetchStoreSettingsQuery
from store.application.services.store_unit_of_work import StoreUnitOfWork
from store.application.store_queries import FetchStoreSettingsQuery
from store.application.store_repository import SqlAlchemyStoreRepository
from store.application.usecases.register_store import RegisterStoreUC, RegisteringStoreResponseBoundary


class StoreModule(injector.Module):
    @injector.provider
    def register_store_uc(self, boundary: RegisteringStoreResponseBoundary, uow: StoreUnitOfWork) -> RegisterStoreUC:
        return RegisterStoreUC(boundary, uow)

    @injector.provider
    def confirm_store_registration_uc(self, boundary: ConfirmingStoreRegistrationResponseBoundary,
                                      uow: StoreUnitOfWork) -> ConfirmStoreRegistrationUC:
        return ConfirmStoreRegistrationUC(boundary, uow)


class StoreInfrastructureModule(injector.Module):
    @injector.provider
    def store_db(self) -> store_db:
        return store_db

    @injector.provider
    def get_uow(self, conn: Connection) -> StoreUnitOfWork:
        sessfactory = sessionmaker(bind=conn)
        return StoreUnitOfWork(sessionfactory=sessfactory)

    @injector.provider
    def fetch_store_settings_query(self, conn: Connection) -> FetchStoreSettingsQuery:
        return SqlFetchStoreSettingsQuery(conn)
