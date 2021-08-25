#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
import itertools
from dataclasses import dataclass
from enum import Enum

from typing import Dict, Optional, List

from shop.application.services.shop_unit_of_work import ShopUnitOfWork
from shop.application.usecases.product.set_shop_products_status_uc import SettingShopProductActions
from shop.application.usecases.shop_uc_common import get_shop_or_raise
from shop.domain.entities.value_objects import ShopBrandId, GenericShopItemStatus
from web_app.serialization.dto import BaseAuthorizedShopUserRequest


@dataclass
class SettingShopBrandsStatusResponse:
    brands: Dict[ShopBrandId, Optional[GenericShopItemStatus]]


class SettingShopBrandsStatusResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: SettingShopBrandsStatusResponse):
        raise NotImplementedError


class SettingShopBrandActions(Enum):
    ENABLE = 'ENABLE'
    DISABLE = 'DISABLE'
    DELETE = 'DELETE'
    UNDELETE = 'UNDELETE'


@dataclass
class SettingShopBrandsStatusRequest(BaseAuthorizedShopUserRequest):
    action: SettingShopBrandActions
    brands: List[ShopBrandId]


class SetShopBrandsStatusUC:
    def __init__(self, ob: SettingShopBrandsStatusResponseBoundary, uow: ShopUnitOfWork):
        self._ob = ob
        self._uow = uow

    def execute(self, dto: SettingShopBrandsStatusRequest):
        with self._uow as uow:
            try:
                shop = get_shop_or_raise(shop_id=dto.shop_id, user_id=dto.current_user_id, uow=uow);

                processed = {brand_id: 'INVALID_ID' for brand_id in dto.brands}
                brands = itertools.filterfalse(lambda b: b.brand_id not in dto.brands, shop.brands)
                brands = [b for b in brands]

                # set the new status is unprocessed if no brand_id found
                for brand in brands:
                    if dto.action == SettingShopBrandActions.DISABLE:
                        if brand.status is GenericShopItemStatus.NORMAL:
                            brand.status = GenericShopItemStatus.DISABLED
                            processed[brand.brand_id] = brand.status
                        else:
                            processed[brand.brand_id] = 'UNPROCESSED'

                    if dto.action == SettingShopBrandActions.ENABLE:
                        if brand.status is GenericShopItemStatus.DISABLED:
                            brand.status = GenericShopItemStatus.NORMAL
                            processed[brand.brand_id] = brand.status
                        else:
                            processed[brand.brand_id] = 'UNPROCESSED'

                    if dto.action == SettingShopBrandActions.DELETE:
                        if brand.status != GenericShopItemStatus.DELETED:
                            brand.status = GenericShopItemStatus.DELETED
                            processed[brand.brand_id] = brand.status
                        else:
                            processed[brand.brand_id] = 'UNPROCESSED'

                    if dto.action == SettingShopBrandActions.UNDELETE:
                        if brand.status == GenericShopItemStatus.DELETED:
                            brand.status = GenericShopItemStatus.NORMAL
                            processed[brand.brand_id] = brand.status
                        else:
                            processed[brand.brand_id] = 'UNPROCESSED'


                response = SettingShopBrandsStatusResponse(brands=processed)
                self._ob.present(response_dto=response)

                shop.version += 1
                uow.commit()
            except Exception as exc:
                raise exc
