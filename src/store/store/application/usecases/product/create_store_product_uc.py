#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from typing import Optional as Opt

from store.application.services.store_unit_of_work import StoreUnitOfWork
from store.application.usecases.store_uc_common import fetch_store_by_owner_or_raise
from store.domain.entities.value_objects import StoreCatalogReference, StoreCollectionReference, StoreProductReference, \
    StoreProductId


@dataclass
class CreatingStoreProductRequest:
    current_user: str

    catalog_reference: Opt[StoreCatalogReference]
    catalog_display_name: Opt[str]
    collection_reference: Opt[StoreCollectionReference]
    collection_display_name: Opt[str]

    reference: Opt[StoreProductReference]
    display_name: str
    image: Opt[str] = ''
    sku: Opt[str] = ''


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
                store = fetch_store_by_owner_or_raise(store_owner=dto.current_user, uow=uow)

                product_data = dict()
                product_data_fields = [
                    'reference',
                    'display_name',
                    'image',
                    'sku',
                    'barcode',
                    'brand_display_name',
                    'seller_phone',
                    'catalog_display_name',
                    'collection_display_name',
                    'unit'
                ]

                # Liệt kê hết tất cả các data field của Product ra đây rồi code.
                # Nếu ví dụ người dùng nhập catalog, collection chưa có trong hệ thống thì kiểm tra và tạo ngay tại đây

                for data_field in product_data_fields:
                    if getattr(dto, data_field, None) is not None:
                        product_data[data_field] = getattr(dto, data_field)

                product = store.make_product(
                    **product_data,
                    catalog_reference=dto.catalog_reference,
                    collection_reference=dto.collection_reference
                )

                # make response
                response_dto = CreatingStoreProductResponse(
                    product_id='product.product_id',
                    product_reference='product.product_reference'
                )
                self._ob.present(response_dto=response_dto)

                # commit
                store.version += 1
                uow.commit()
            except Exception as exc:
                raise exc
