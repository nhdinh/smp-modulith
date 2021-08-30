#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
import itertools
from dataclasses import dataclass
from enum import Enum

from typing import Dict, Optional, List

from shop.application.services.shop_unit_of_work import ShopUnitOfWork
from shop.application.usecases.shop_uc_common import get_shop_or_raise
from shop.domain.entities.value_objects import ShopCatalogId, GenericShopItemStatus
from web_app.serialization.dto import BaseAuthorizedShopUserRequest


@dataclass
class SettingShopCatalogsStatusResponse:
    catalogs: Dict[ShopCatalogId, Optional[GenericShopItemStatus]]


class SettingShopCatalogsStatusResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: SettingShopCatalogsStatusResponse):
        raise NotImplementedError


class SettingShopCatalogActions(Enum):
    ENABLE = 'ENABLE'
    DISABLE = 'DISABLE'
    DELETE = 'DELETE'
    UNDELETE = 'UNDELETE'


@dataclass
class SettingShopCatalogsStatusRequest(BaseAuthorizedShopUserRequest):
    action: SettingShopCatalogActions
    catalogs: List[ShopCatalogId]


class SetShopCatalogsStatusUC:
    def __init__(self, ob: SettingShopCatalogsStatusResponseBoundary, uow: ShopUnitOfWork):
        self._ob = ob
        self._uow = uow

    def execute(self, dto: SettingShopCatalogsStatusRequest):
        with self._uow as uow:  # type:ShopUnitOfWork
            try:
                shop = get_shop_or_raise(shop_id=dto.shop_id, user_id=dto.current_user_id, uow=uow)

                processed = {catalog_id: 'INVALID_ID' for catalog_id in dto.catalogs}
                catalogs = list(
                    itertools.filterfalse(lambda c: c.catalog_id not in dto.catalogs or c.default, shop.catalogs))

                # set the new status is unprocessed if no catalog_id found
                for catalog in catalogs:
                    if dto.action == SettingShopCatalogActions.DISABLE:
                        if catalog.status is GenericShopItemStatus.NORMAL:
                            catalog.status = GenericShopItemStatus.DISABLED
                            processed[catalog.catalog_id] = catalog.status
                        else:
                            processed[catalog.catalog_id] = 'UNPROCESSED'

                    if dto.action == SettingShopCatalogActions.ENABLE:
                        if catalog.status is GenericShopItemStatus.DISABLED:
                            catalog.status = GenericShopItemStatus.NORMAL
                            processed[catalog.catalog_id] = catalog.status
                        else:
                            processed[catalog.catalog_id] = 'UNPROCESSED'

                    if dto.action == SettingShopCatalogActions.DELETE:
                        if catalog.status != GenericShopItemStatus.DELETED:
                            catalog.status = GenericShopItemStatus.DELETED
                            processed[catalog.catalog_id] = catalog.status
                        else:
                            processed[catalog.catalog_id] = 'UNPROCESSED'

                    if dto.action == SettingShopCatalogActions.UNDELETE:
                        if catalog.status == GenericShopItemStatus.DELETED:
                            catalog.status = GenericShopItemStatus.NORMAL
                            processed[catalog.catalog_id] = catalog.status
                        else:
                            processed[catalog.catalog_id] = 'UNPROCESSED'

                response = SettingShopCatalogsStatusResponse(catalogs=processed)
                self._ob.present(response_dto=response)

                shop.version += 1
                uow.commit()
            except Exception as exc:
                raise exc
