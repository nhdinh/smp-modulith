#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from foundation.events import ThingGoneInBlackHoleError
from foundation.fs import FileSystem
from shop.application.services.shop_unit_of_work import ShopUnitOfWork
from shop.application.usecases.shop_uc_common import get_product_by_id_or_raise, get_shop_or_raise
from shop.domain.entities.value_objects import ExceptionMessages, ShopProductAttributeTypes, ShopProductId
from shop.domain.events import ShopProductUpdatedEvent


@dataclass
class RemovingStoreProductAttributeRequest:
    current_user: str
    product_id: ShopProductId
    attribute_type: ShopProductAttributeTypes
    attribute_id: str


@dataclass
class RemovingStoreProductAttributeResponse:
    status: bool


class RemovingStoreProductAttributeResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: RemovingStoreProductAttributeResponse):
        raise NotImplementedError


class RemoveStoreProductAttributeUC:
    def __init__(self, boundary: RemovingStoreProductAttributeResponseBoundary, uow: ShopUnitOfWork, fs: FileSystem):
        self._ob = boundary
        self._uow = uow
        self._fs = fs

    def execute(self, dto: RemovingStoreProductAttributeRequest):
        with self._uow as uow:  # type:ShopUnitOfWork
            try:
                store = get_shop_or_raise(store_owner=dto.current_user, uow=uow)
                product = get_product_by_id_or_raise(product_id=dto.product_id, uow=uow)

                if not product.is_belong_to_shop(store):
                    raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_PRODUCT_NOT_FOUND)

                # remove collection
                if dto.attribute_type == ShopProductAttributeTypes.COLLECTIONS:
                    try:
                        collection = next(c for c in product.collections if c.collection_id == dto.attribute_id)
                        product.collections.remove(collection)
                    except StopIteration:
                        raise ValueError(ExceptionMessages.SHOP_COLLECTION_NOT_FOUND)

                # remove supplier
                if dto.attribute_type == ShopProductAttributeTypes.SUPPLIERS:
                    try:
                        supplier = next(s for s in product.suppliers if s.supplier_id == dto.attribute_id)

                        product_prices = product.get_prices(by_supplier=supplier)
                        product.suppliers.remove(supplier)
                    except StopIteration:
                        raise ValueError(ExceptionMessages.SHOP_SUPPLIER_NOT_FOUND)

                response_dto = RemovingStoreProductAttributeResponse(status=True)
                self._ob.present(response_dto=response_dto)

                # raise event
                store.domain_events.append(ShopProductUpdatedEvent(product_id=product.product_id))

                store.version += 1
                uow.commit()
            except Exception as exc:
                raise exc
