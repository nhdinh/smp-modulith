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
    title: str

    # product data (options)
    reference: Opt[StoreProductReference] = None
    image: Opt[str] = None
    sku: Opt[str] = None
    barcode: Opt[str] = None

    # tags (optional)
    tags: Opt[List[str]] = field(default_factory=list)
    # tags: Opt[List[str]] = fields.List(fields.Str(required=False), required=False)

    # brands (optional)
    brand: Opt[str] = None

    # seller (optional)
    seller_phone: Opt[str] = None
    seller_contact_name: Opt[str] = None

    # catalog & collection (optional)
    catalog: Opt[str] = None
    collections: Opt[List[str]] = field(default_factory=list)

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
                    'title',

                    # product data (optional)
                    'reference',
                    'image',
                    'sku',
                    'barcode',

                    # tags
                    'tags',

                    # brand
                    'brand',

                    # seller
                    'seller_phone',
                    'seller_contact_name',

                    # catalog
                    'catalog',

                    # collection
                    'collections',

                    # unit & first stocking
                    'default_unit',
                    'first_inventory_stocking',

                    # conversion units
                    'unit_conversions',
                    'first_inventory_stocking_for_unit_conversions',
                ]

                for data_field in product_data_fields:
                    if getattr(dto, data_field, None) is not None:
                        data = getattr(dto, data_field)

                        # process array data
                        if data_field == 'unit_conversions':  # unit_conversions
                            unit_conversions = []
                            for unit_conversion in data:  # type:CreatingStoreProductUnitConversionRequest
                                unit_conversions.append({
                                    'unit': unit_conversion.unit,
                                    'base_unit': unit_conversion.base_unit,
                                    'conversion_factor': unit_conversion.conversion_factor,
                                })

                            data = unit_conversions

                        product_data[data_field] = data

                product = store.create_product(**product_data)

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
            finally:
                # uow.rollback()
                pass
