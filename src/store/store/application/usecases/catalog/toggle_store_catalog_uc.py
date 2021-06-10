#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from store.application.services.store_unit_of_work import StoreUnitOfWork
from store.application.usecases.const import ExceptionMessages
from store.application.usecases.store_uc_common import fetch_store_by_id, validate_store_ownership
from store.application.usecases.catalog.update_store_catalog_uc import UpdatingStoreCatalogResponseBoundary, \
    UpdatingStoreCatalogResponse
from store.domain.entities.value_objects import StoreId, StoreCatalogReference


@dataclass
class TogglingStoreCatalogRequest:
    store_id: StoreId
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
                store = fetch_store_by_id(store_id=input_dto.store_id, uow=uow)
                if store is None:
                    raise Exception(ExceptionMessages.STORE_NOT_FOUND)

                # if the Store is disabled by admin
                if getattr(store, 'disabled', False):
                    raise Exception(ExceptionMessages.STORE_NOT_AVAILABLE)

                if not validate_store_ownership(store=store, owner_email=input_dto.current_user):
                    raise Exception(ExceptionMessages.CURRENT_USER_DO_NOT_HAVE_PERMISSION_ON_STORE)

                # check catalog
                if not store.has_catalog(catalog_reference=input_dto.catalog_reference):
                    raise Exception(ExceptionMessages.STORE_CATALOG_NOT_FOUND)

                # do update
                store.toggle_catalog(catalog_reference=input_dto.catalog_reference)

                # build the output
                response_dto = UpdatingStoreCatalogResponse(
                    store_id=store.store_id,
                    catalog_reference=input_dto.catalog_reference,
                    status=True
                )
                self._ob.present(response_dto=response_dto)

                # commit
                uow.commit()
            except Exception as exc:
                raise exc
