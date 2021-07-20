#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from foundation.events import ThingGoneInBlackHoleError

from shop.application.services.shop_unit_of_work import ShopUnitOfWork
from shop.application.usecases.catalog.update_shop_catalog_uc import UpdatingShopCatalogResponseBoundary
from shop.application.usecases.shop_uc_common import validate_shop
from shop.domain.entities.shop import Shop
from shop.domain.entities.value_objects import ExceptionMessages, ShopCatalogId


@dataclass
class TogglingStoreCatalogRequest:
    current_user: str
    catalog_id: ShopCatalogId


class ToggleStoreCatalogUC:
    def __init__(self, ob: UpdatingShopCatalogResponseBoundary, uow: ShopUnitOfWork):
        self._ob = ob
        self._uow = uow

    def execute(self, input_dto: TogglingStoreCatalogRequest):
        with self._uow as uow:  # type:ShopUnitOfWork
            try:
                # fetch store data by id ID
                store = uow.shops.get_shop_by_email(email=input_dto.current_user)
                if store is None:
                    raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_NOT_FOUND)

                # if the Store is disabled by admin
                if ToggleStoreCatalogUC._is_store_disabled(store):
                    raise Exception(ExceptionMessages.SHOP_NOT_AVAILABLE)

                if not validate_shop(store=store, owner_email=input_dto.current_user):
                    raise Exception(ExceptionMessages.CURRENT_USER_DO_NOT_HAVE_PERMISSION_ON_SHOP)

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
