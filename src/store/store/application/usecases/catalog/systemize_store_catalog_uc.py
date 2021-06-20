#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from store.application.services.store_unit_of_work import StoreUnitOfWork
from store.application.usecases.catalog.update_store_catalog_uc import UpdatingStoreCatalogResponse, \
    UpdatingStoreCatalogResponseBoundary
from store.application.usecases.store_uc_common import fetch_store_by_owner_or_raise
from store.domain.entities.value_objects import StoreCatalogReference


@dataclass
class SystemizingStoreCatalogRequest:
    current_user: str
    catalog_reference: StoreCatalogReference


class SystemizeStoreCatalogUC:
    def __init__(self, boundary: UpdatingStoreCatalogResponseBoundary, uow: StoreUnitOfWork):
        self._ob = boundary
        self._uow = uow

    def execute(self, dto: SystemizingStoreCatalogRequest):
        with self._uow as uow:  # type: StoreUnitOfWork
            try:
                store = fetch_store_by_owner_or_raise(store_owner=dto.current_user, uow=uow)

                store.make_system_catalog(catalog_reference=dto.catalog_reference)

                response_dto = UpdatingStoreCatalogResponse(status=True)
                self._ob.present(response_dto=response_dto)

                # commit
                uow.commit()
            except Exception as exc:
                raise exc
