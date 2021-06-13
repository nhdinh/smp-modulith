#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import insert, delete

from store.adapter.store_db import store_catalog_cache_table
from store.application.services.store_unit_of_work import StoreUnitOfWork
from store.application.usecases.const import ExceptionMessages
from store.application.usecases.store_uc_common import GenericStoreActionRequest, GenericStoreResponseBoundary, \
    GenericStoreActionResponse
from store.domain.entities.store import Store


class InvalidateStoreCatalogCacheUC:
    def __init__(self, ob: GenericStoreResponseBoundary, uow: StoreUnitOfWork):
        self._ob = ob
        self._uow = uow

    def execute(self, dto: GenericStoreActionRequest) -> None:
        with self._uow as uow:  # type: StoreUnitOfWork
            try:
                store = uow.stores.fetch_store_of_owner(dto.current_user)  # type:Store

                if not store:
                    raise Exception(ExceptionMessages.STORE_NOT_FOUND)

                # remove all old cache data
                q = delete(store_catalog_cache_table).where(store_catalog_cache_table.c.store_id == store.store_id)
                uow.session.execute(q)

                # update new cache
                q = insert(store_catalog_cache_table).values([
                    {
                        'store_id': store.store_id,
                        'catalog_id': catalog.catalog_id,
                        'catalog_reference': catalog.reference
                    } for catalog in store.catalogs
                ])
                uow.session.execute(q)

                # build response
                response_dto = GenericStoreActionResponse(status=True)
                self._ob.present(response_dto)

                # commit the data
                uow.commit()
            except Exception as exc:
                raise exc
