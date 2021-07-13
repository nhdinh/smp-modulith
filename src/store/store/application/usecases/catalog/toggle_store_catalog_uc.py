#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from store.application.services.store_unit_of_work import StoreUnitOfWork
from store.application.usecases.catalog.update_store_catalog_uc import UpdatingStoreCatalogResponseBoundary, \
    UpdatingStoreCatalogResponse
from store.application.usecases.const import ExceptionMessages, ThingGoneInBlackHoleError
from store.application.usecases.store_uc_common import validate_store_ownership
from store.domain.entities.shop import Shop
from store.domain.entities.value_objects import StoreCatalogId


@dataclass
class TogglingStoreCatalogRequest:
    current_user: str
    catalog_id: StoreCatalogId


class ToggleStoreCatalogUC:
    def __init__(self, ob: UpdatingStoreCatalogResponseBoundary, uow: StoreUnitOfWork):
        self._ob = ob
        self._uow = uow

    def execute(self, input_dto: TogglingStoreCatalogRequest):
        with self._uow as uow:  # type:StoreUnitOfWork
            try:
                # fetch store data by id ID
                store = uow.shops.get_shop_by_email(email=input_dto.current_user)
                if store is None:
                    raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_NOT_FOUND)

                # if the Store is disabled by admin
                if ToggleStoreCatalogUC._is_store_disabled(store):
                    raise Exception(ExceptionMessages.SHOP_NOT_AVAILABLE)

                if not validate_store_ownership(store=store, owner_email=input_dto.current_user):
                    raise Exception(ExceptionMessages.CURRENT_USER_DO_NOT_HAVE_PERMISSION_ON_STORE)

                raise NotImplementedError

                # build the output
                response_dto = UpdatingStoreCatalogResponse(status=True)
                self._ob.present(response_dto=response_dto)

                # commit
                uow.commit()
            except Exception as exc:
                raise exc

    @classmethod
    def _is_store_disabled(cls, store: Shop):
        return getattr(store, 'disabled', False)
