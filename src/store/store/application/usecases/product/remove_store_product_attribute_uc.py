#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from store.domain.events.store_product_events import StoreProductUpdatedEvent

from foundation.fs import FileSystem
from store.application.services.store_unit_of_work import StoreUnitOfWork
from store.application.usecases.const import ThingGoneInBlackHoleError, ExceptionMessages
from store.application.usecases.store_uc_common import get_shop_or_raise, get_product_by_id_or_raise
from store.domain.entities.store_product import StoreProductAttributeTypes
from store.domain.entities.value_objects import ShopProductId


@dataclass
class RemovingStoreProductAttributeRequest:
    current_user: str
    product_id: ShopProductId
    attribute_type: StoreProductAttributeTypes
    attribute_id: str


@dataclass
class RemovingStoreProductAttributeResponse:
    status: bool


class RemovingStoreProductAttributeResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: RemovingStoreProductAttributeResponse):
        raise NotImplementedError


class RemoveStoreProductAttributeUC:
    def __init__(self, boundary: RemovingStoreProductAttributeResponseBoundary, uow: StoreUnitOfWork, fs: FileSystem):
        self._ob = boundary
        self._uow = uow
        self._fs = fs

    def execute(self, dto: RemovingStoreProductAttributeRequest):
        with self._uow as uow:  # type:StoreUnitOfWork
            try:
                store = get_shop_or_raise(store_owner=dto.current_user, uow=uow)
                product = get_product_by_id_or_raise(product_id=dto.product_id, uow=uow)

                if not product.is_belong_to_store(store):
                    raise ThingGoneInBlackHoleError(ExceptionMessages.STORE_PRODUCT_NOT_FOUND)

                # remove collection
                if dto.attribute_type == StoreProductAttributeTypes.COLLECTIONS:
                    try:
                        collection = next(c for c in product.collections if c.collection_id == dto.attribute_id)
                        product.collections.remove(collection)
                    except StopIteration:
                        raise ValueError(ExceptionMessages.STORE_COLLECTION_NOT_FOUND)

                # remove supplier
                if dto.attribute_type == StoreProductAttributeTypes.SUPPLIERS:
                    try:
                        supplier = next(s for s in product.suppliers if s.supplier_id == dto.attribute_id)

                        product_prices = product.get_prices(by_supplier=supplier)
                        product.suppliers.remove(supplier)
                    except StopIteration:
                        raise ValueError(ExceptionMessages.STORE_SUPPLIER_NOT_FOUND)

                response_dto = RemovingStoreProductAttributeResponse(status=True)
                self._ob.present(response_dto=response_dto)

                # raise event
                store.domain_events.append(StoreProductUpdatedEvent(product_id=product.product_id))

                store.version += 1
                uow.commit()
            except Exception as exc:
                raise exc
