#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from typing import List, Optional as Opt

from foundation.events import ThingGoneInBlackHoleError
from foundation.fs import FileSystem
from shop.application.services.shop_unit_of_work import ShopUnitOfWork
from shop.application.usecases.shop_uc_common import get_product_by_id_or_raise, get_shop_or_raise
from shop.domain.entities.value_objects import ShopProductId, ExceptionMessages
from web_app.serialization.dto import BaseAuthorizedShopUserRequest


@dataclass
class UpdatingStoreProductRequest(BaseAuthorizedShopUserRequest):
    current_user: str
    product_id: ShopProductId

    title: Opt[str]
    sku: Opt[str]
    barcode: Opt[str]
    image: Opt[str]

    brand: Opt[str]
    collections: Opt[List[str]]


@dataclass
class UpdatingStoreProductResponse:
    status: bool


class UpdatingStoreProductResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: UpdatingStoreProductResponse):
        raise NotImplementedError


class UpdateStoreProductUC:
    def __init__(self, boundary: UpdatingStoreProductResponseBoundary, uow: ShopUnitOfWork, fs: FileSystem):
        self._ob = boundary
        self._uow = uow
        self._fs = fs

    def execute(self, dto: UpdatingStoreProductRequest) -> None:
        with self._uow as uow:  # type:ShopUnitOfWork
            try:
                store = get_shop_or_raise(shop_id=dto.shop_id, user_id=dto.current_user_id, uow=uow)
                product = get_product_by_id_or_raise(product_id=dto.product_id, uow=uow)

                if not product.is_belong_to_shop(store):
                    raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_PRODUCT_NOT_FOUND)

                update_data = {}

                if dto.title is not None:
                    update_data['title'] = dto.title

                if dto.brand is not None:
                    update_data['brand'] = dto.brand

                if dto.collections is not None:
                    update_data['collections'] = dto.collections

                store.update_product(product=product, **update_data)

                response_dto = UpdatingStoreProductResponse(status=True)
                self._ob.present(response_dto=response_dto)


                store.version += 1

                uow.commit()
            except Exception as exc:
                raise exc
