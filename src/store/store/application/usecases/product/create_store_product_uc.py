#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
import random
import string
from dataclasses import dataclass, field
from datetime import date
from typing import Optional as Opt, List

from dateutil.utils import today
from sqlalchemy import insert
from sqlalchemy.engine.row import RowProxy
from sqlalchemy.exc import IntegrityError
from store.application.store_handler_facade import StoreHandlerFacade

from store.adapter.store_db import store_product_data_cache_table
from store.application.services.store_unit_of_work import StoreUnitOfWork
from store.application.usecases.store_uc_common import fetch_store_by_owner_or_raise
from store.domain.entities.store_product import StoreProductId, StoreProductReference, StoreProduct


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
class CreatingProductPriceRequest:
    unit: str
    price: float
    currency: Opt[str]
    tax: Opt[float]
    effective_from: date = today()


@dataclass(frozen=True)
class CreatingStoreSupplierRequest:
    supplier_name: str
    contact_name: Opt[str]
    contact_phone: Opt[str]
    purchase_prices: Opt[List[CreatingProductPriceRequest]] = field(default_factory=list)


@dataclass(frozen=True)
class CreatingStoreProductRequest:
    current_user: str

    # product data (mandatory)
    title: str
    sku: str
    default_unit: str

    # product data (options)
    reference: Opt[StoreProductReference] = None
    image: Opt[str] = None
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
    collections: Opt[List[str]] = field(default_factory=list),

    # threshold(s)
    restock_threshold: Opt[int] = 0
    max_stock_threshold: Opt[int] = 0

    # conversion units (optional)
    unit_conversions: Opt[List[CreatingStoreProductUnitConversionRequest]] = field(default_factory=list)
    first_inventory_stocking_for_unit_conversions: Opt[List[CreatingStoreProductFirstStockingRequest]] = field(
        default_factory=list)

    suppliers: Opt[List[CreatingStoreSupplierRequest]] = field(default_factory=list)


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

                    # suppliers
                    'suppliers',

                    # catalog
                    'catalog',

                    # collection
                    'collections',

                    # unit & first stocking
                    'default_unit',

                    # conversion units
                    'unit_conversions',
                    'first_inventory_stocking_for_unit_conversions',

                    # thresholds
                    'restock_threshold',
                    'max_stock_threshold',
                ]

                for data_field in product_data_fields:
                    data = None

                    # get data from dto
                    if getattr(dto, data_field, None) is not None:
                        data = getattr(dto, data_field)

                        # process units array data
                        if data_field == 'unit_conversions':  # unit_conversions
                            unit_conversions = []
                            for unit_conversion in data:  # type:CreatingStoreProductUnitConversionRequest
                                unit_conversions.append({
                                    'unit': unit_conversion.unit,
                                    'base_unit': unit_conversion.base_unit,
                                    'conversion_factor': unit_conversion.conversion_factor,
                                })

                            data = unit_conversions

                        # process stocking data
                        elif data_field == 'first_inventory_stocking_for_unit_conversions':
                            stockings = []
                            for stocking in data:  # type:CreatingStoreProductFirstStockingRequest
                                stockings.append({
                                    'unit': stocking.unit,
                                    'stocking': stocking.stocking,
                                })
                            data = stockings

                        # process suppliers data
                        elif data_field == 'suppliers':
                            suppliers = []
                            for create_supplier_request in data:  # type:CreatingStoreSupplierRequest
                                supplier_prices = []
                                for create_price_request in create_supplier_request.purchase_prices:  # type:CreatingProductPriceRequest
                                    supplier_prices.append({
                                        'supplier_name': create_supplier_request.supplier_name,
                                        'unit': create_price_request.unit,
                                        'price': create_price_request.price,
                                        'currency': create_price_request.currency,
                                        'tax': create_price_request.tax,
                                        'effective_from': create_price_request.effective_from
                                    })

                                suppliers.append({
                                    'supplier_name': create_supplier_request.supplier_name,
                                    'contact_name': create_supplier_request.contact_name,
                                    'contact_phone': create_supplier_request.contact_phone,
                                    'supplier_prices': supplier_prices
                                })

                            data = suppliers

                    # add processed data back to product_data
                    if data is not None:
                        product_data[data_field] = data

                # TODO: Remove after test
                product_data['title'] += ''.join(random.sample(string.ascii_lowercase, 8))
                product_data['sku'] += ''.join(random.sample(string.ascii_uppercase, 3))

                product = store.create_product(**product_data)

                # make response
                response_dto = CreatingStoreProductResponse(
                    product_id=product.product_id,
                    product_reference=product.reference
                )
                self._ob.present(response_dto=response_dto)

                # increase aggregate version
                store.version += 1

                handler = StoreHandlerFacade(connection=uow.session.connection())
                handler.update_store_product_cache(product_id=product.product_id)
                uow.commit()
            except IntegrityError as exc:
                raise exc
            except Exception as exc:
                raise exc
