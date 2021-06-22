#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass, field
from typing import Optional as Opt, List

from marshmallow import fields

from store.application.services.store_unit_of_work import StoreUnitOfWork
from store.application.usecases.store_uc_common import fetch_store_by_owner_or_raise
from store.domain.entities.value_objects import StoreCatalogReference, StoreCollectionReference, StoreProductReference, \
    StoreProductId


@dataclass(frozen=True)
class CreatingStoreProductUnitConversionRequest:
    unit: str
    base_unit: str
    conversion_factor: float


@dataclass(frozen=True)
class CreatingStoreProductFirstStockingRequest:
    unit: str
    stocking: int


@dataclass(frozen=True)
class CreatingStoreProductRequest:
    current_user: str

    # product data (mandatory)
    display_name: str

    # product data (options)
    reference: Opt[StoreProductReference] = None
    image: Opt[str] = None
    sku: Opt[str] = None
    barcode: Opt[str] = None

    # tags (optional)
    tags: Opt[List[str]] = field(default_factory=list)
    # tags: Opt[List[str]] = fields.List(fields.Str(required=False), required=False)

    # brands (optional)
    brand_display_name: Opt[str] = None
    brand_reference: Opt[str] = None

    # seller (optional)
    seller_phone: Opt[str] = None
    seller_contact_name: Opt[str] = None

    # catalog & collection (optional)
    catalog_reference: Opt[StoreCatalogReference] = None
    catalog_display_name: Opt[str] = None
    collection_reference: Opt[StoreCollectionReference] = None
    collection_display_name: Opt[str] = None

    # unit & first stocking (optional)
    default_unit: Opt[str] = None
    first_inventory_stocking: Opt[int] = None

    # conversion units (optional)
    unit_conversions: Opt[List[CreatingStoreProductUnitConversionRequest]] = field(default_factory=list)
    first_inventory_stocking_for_unit_conversions: Opt[List[CreatingStoreProductFirstStockingRequest]] = field(
        default_factory=list)


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
                    # product data (required)
                    'display_name',

                    # product data (optional)
                    'reference',
                    'image',
                    'sku',
                    'barcode',

                    # tags
                    'tags',

                    # brand
                    'brand_display_name',
                    'brand_reference',

                    # seller
                    'seller_phone',
                    'seller_contact_name',

                    # catalog
                    'catalog_display_name',
                    'catalog_reference',

                    # collection
                    'collection_display_name',
                    'collection_reference',

                    # unit & first stocking
                    'default_unit',
                    'first_inventory_stocking',

                    # conversion units
                    'unit_conversions',
                    'first_inventory_stocking_for_unit_conversions',
                ]

                for data_field in product_data_fields:
                    if getattr(dto, data_field, None) is not None:
                        product_data[data_field] = getattr(dto, data_field)

                product = store.make_product(**product_data)

                # make response
                response_dto = CreatingStoreProductResponse(
                    product_id=product.product_id,
                    product_reference=product.reference
                )
                self._ob.present(response_dto=response_dto)

                # increase aggregate version
                store.version += 1
                uow.commit()
            except Exception as exc:
                raise exc
