#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from store.application.services.store_unit_of_work import StoreUnitOfWork
from store.application.usecases.catalog.update_store_catalog_uc import UpdatingStoreCatalogResponseBoundary, \
    UpdatingStoreCatalogResponse
from store.application.usecases.const import ExceptionMessages, ExceptionWhileFindingThingInBlackHole
from store.application.usecases.store_uc_common import validate_store_ownership
from store.domain.entities.store import Store
from store.domain.entities.store_catalog import StoreCatalogReference


@dataclass
class TogglingStoreCatalogRequest:
    current_user: str
    catalog_reference: StoreCatalogReference


class ToggleStoreCatalogUC:
    def __init__(self, ob: UpdatingStoreCatalogResponseBoundary, uow: StoreUnitOfWork):
        self._ob = ob
        self._uow = uow

    def execute(self, input_dto: TogglingStoreCatalogRequest):
        with self._uow as uow:  # type:StoreUnitOfWork
            try:
                # fetch store data by id ID
                store = uow.stores.fetch_store_of_owner(owner=input_dto.current_user)
                if store is None:
                    raise ExceptionWhileFindingThingInBlackHole(ExceptionMessages.STORE_NOT_FOUND)

                # if the Store is disabled by admin
                if ToggleStoreCatalogUC._is_store_disabled(store):
                    raise Exception(ExceptionMessages.STORE_NOT_AVAILABLE)

                if not validate_store_ownership(store=store, owner_email=input_dto.current_user):
                    raise Exception(ExceptionMessages.CURRENT_USER_DO_NOT_HAVE_PERMISSION_ON_STORE)

                # check catalog
                if not store.contains_catalog_reference(catalog_reference=input_dto.catalog_reference):
                    raise ExceptionWhileFindingThingInBlackHole(ExceptionMessages.STORE_CATALOG_NOT_FOUND)

                # check if catalog is system type
                catalog = store.fetch_catalog_by_id_or_reference(search_term=input_dto.catalog_reference)
                if catalog.system:
                    raise Exception(ExceptionMessages.SYSTEM_STORE_CATALOG_CANNOT_BE_DISABLED)

                # do update
                store.toggle_catalog(catalog_reference=input_dto.catalog_reference)

                # build the output
                response_dto = UpdatingStoreCatalogResponse(status=True)
                self._ob.present(response_dto=response_dto)

                # commit
                uow.commit()
            except Exception as exc:
                raise exc

    @classmethod
    def _is_store_disabled(cls, store: Store):
        return getattr(store, 'disabled', False)
