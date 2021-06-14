#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from typing import Optional

from store.application.services.store_unit_of_work import StoreUnitOfWork
from store.application.usecases.store_uc_common import fetch_store_by_owner
from store.domain.entities.value_objects import StoreCatalogReference, StoreCollectionReference, StoreProductReference, \
    StoreProductId


@dataclass
class CreatingStoreProductRequest:
    current_user: str
    catalog_reference: StoreCatalogReference
    collection_reference: StoreCollectionReference

    product_reference: StoreProductReference
    product_display_name: str
    product_image: Optional[str] = ''
    product_sku: Optional[str] = ''


@dataclass
class CreatingStoreProductResponse:
    product_id: StoreProductId
    product_reference: StoreProductReference


class CreatingStoreProductResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: CreatingStoreProductResponse):
        raise NotImplementedError


class CreateStoreProductUC:
    def __init__(self, boundary: CreatingStoreProductResponseBoundary, uow: StoreUnitOfWork):
        self._ob = boundary
        self._uow = uow

    def execute(self, dto: CreatingStoreProductRequest) -> None:
        with self._uow as uow:  # type:StoreUnitOfWork
            try:
                store = fetch_store_by_owner(store_owner=dto.current_user)

                product_data = dict()
                product_data_fields = [
                    'display_name',
                    'image',
                    'sku',
                ]

                # Liệt kê hết tất cả các data field của Product ra đây rồi code. Nếu ví dụ người dùng nhập catalog, collection chưa có trong hệ thống thì kiểm tra và tạo ngay tại đây

                for data_field in product_data_fields:
                    if getattr(dto, f'product_{data_field}', None) is not None:
                        product_data[data_field] = getattr(dto, f'product_{data_field}')

                product = store.make_product(
                    **product_data,
                    catalog_reference=dto.catalog_reference,
                    collection_reference=dto.collection_reference
                )

                # make response
                response_dto = CreatingStoreProductResponse(
                    product_id=product.product_id,
                    product_reference=product.product_reference
                )
                self._ob.present(response_dto=response_dto)

                # commit
                uow.commit()
            except Exception as exc:
                raise exc
