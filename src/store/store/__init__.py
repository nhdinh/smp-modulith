#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector

from store.adapter import store_db
from store.application.usecases.register_store import RegisterStoreUC, RegisteringStoreResponseBoundary


class StoreModule(injector.Module):
    @injector.provider
    def register_store_uc(self, boundary: RegisteringStoreResponseBoundary, uow: StoreUnitOfWork) -> RegisterStoreUC:
        return RegisterStoreUC(boundary, uow)


class StoreInfrastructureModule(injector.Module):
    @injector.provider
    def store_db(self) -> store_db:
        return store_db
