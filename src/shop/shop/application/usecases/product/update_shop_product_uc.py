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
class UpdatingShopProductRequest(BaseAuthorizedShopUserRequest):
    product_id: ShopProductId

    title: Opt[str]
    sku: Opt[str]
    barcode: Opt[str]
    image: Opt[str]
    description: Opt[str]

    catalog_id: Opt[str]
    brand_id: Opt[str]
    default_unit: Opt[str]

    collection_indexes: Opt[List[str]]

    restock_threshold: Opt[int]
    maxstock_threshold: Opt[int]

    status: Opt[str]
    tags: Opt[List[str]]


@dataclass
class UpdatingShopProductResponse:
    status: bool


class UpdatingShopProductResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: UpdatingShopProductResponse):
        raise NotImplementedError


class UpdateShopProductUC:
    def __init__(self, boundary: UpdatingShopProductResponseBoundary, uow: ShopUnitOfWork, fs: FileSystem):
        self._ob = boundary
        self._uow = uow
        self._fs = fs

    def execute(self, dto: UpdatingShopProductRequest) -> None:
        with self._uow as uow:  # type:ShopUnitOfWork
            try:
                shop = get_shop_or_raise(shop_id=dto.shop_id, user_id=dto.current_user_id, uow=uow)
                product = get_product_by_id_or_raise(product_id=dto.product_id, uow=uow)

                if not product.is_belong_to_shop(shop):
                    raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_PRODUCT_NOT_FOUND)

                update_data = {
                    'title': dto.title if dto.title else None,
                    'sku': dto.sku if dto.sku else None,
                    'barcode': dto.barcode if dto.barcode else None,
                    'image': dto.image if dto.image else None,
                    'description': dto.description if dto.description else None,

                    'catalog_id': dto.catalog_id if dto.catalog_id else None,
                    'brand_id': dto.brand_id if dto.brand_id else None,

                    'collection_indexes': dto.collection_indexes if dto.collection_indexes else None,
                    'restock_threshold': dto.restock_threshold if dto.restock_threshold else -1,
                    'maxstock_threshold': dto.maxstock_threshold if dto.maxstock_threshold else -1,

                    'status': dto.status if dto.status else None,
                    'tags': dto.tags if dto.tags else None
                }

                shop.update_product(product=product, **update_data)

                response_dto = UpdatingShopProductResponse(status=True)
                self._ob.present(response_dto=response_dto)

                shop.version += 1

                uow.commit()
            except Exception as exc:
                raise exc
