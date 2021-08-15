#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import string
from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional as Opt, Union

import nanoid
from dateutil.utils import today
from sqlalchemy.exc import IntegrityError

from shop.application.services.shop_unit_of_work import ShopUnitOfWork
from shop.application.usecases.shop_uc_common import get_shop_or_raise
from shop.domain.entities.value_objects import ShopProductId, ExceptionMessages
from web_app.serialization.dto import BaseAuthorizedShopUserRequest


@dataclass(frozen=True)
class CreatingShopProductUnitConversionRequest:
    unit: str
    base_unit: str
    conversion_factor: float


@dataclass(frozen=True)
class CreatingShopProductFirstStockingRequest:
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
class CreatingShopSupplierWithPurchasePriceRequest:
    supplier_name: str
    contact_name: Opt[str]
    contact_phone: Opt[str]
    purchase_prices: Opt[List[CreatingProductPriceRequest]] = field(default_factory=list)


@dataclass
class AddingShopProductRequest(BaseAuthorizedShopUserRequest):
    # product data (mandatory)
    title: str
    sku: str
    default_unit: str

    pending: Opt[str] = 'False'

    # product data (options)
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
    catalog_id: Opt[str] = None
    catalog: Opt[str] = None
    collections: Opt[List[str]] = field(default_factory=list)

    # threshold(s)
    restock_threshold: Opt[int] = 0
    max_stock_threshold: Opt[int] = 0

    # conversion units (optional)
    unit_conversions: Opt[List[CreatingShopProductUnitConversionRequest]] = field(default_factory=list)
    first_inventory_stocking_for_unit_conversions: Opt[List[CreatingShopProductFirstStockingRequest]] = field(
        default_factory=list)

    suppliers: Opt[List[CreatingShopSupplierWithPurchasePriceRequest]] = field(default_factory=list)


@dataclass
class AddingShopPendingProductRequest(BaseAuthorizedShopUserRequest):
    pending: Opt[str] = None


@dataclass
class AddingShopProductResponse:
    product_id: ShopProductId


class AddingShopProductResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: AddingShopProductResponse):
        raise NotImplementedError


class AddShopProductUC:
    PRODUCT_DATA_FIELDS = [
        # product data (required)
        'title',

        # product data (optional)
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
        'catalog_id',
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

    def __init__(self, boundary: AddingShopProductResponseBoundary, uow: ShopUnitOfWork):
        self._ob = boundary
        self._uow = uow

    def execute(self, dto: Union[AddingShopProductRequest, AddingShopPendingProductRequest]) -> None:
        with self._uow as uow:  # type:ShopUnitOfWork
            try:
                shop = get_shop_or_raise(shop_id=dto.shop_id, user_id=dto.current_user_id, uow=uow)

                if isinstance(dto, AddingShopPendingProductRequest) and dto.pending == 'True':
                    title = 'PENDING_PRODUCT'
                    sku = 'PENDING_SKU_' + nanoid.generate(string.ascii_letters, size=5)
                    default_unit = 'PENDING_UNIT'

                    # add pending product and return productId
                    product = shop.create_product(**{
                        'title': title,
                        'sku': sku,
                        'default_unit': default_unit,
                        'pending': True
                    })
                elif isinstance(dto, AddingShopProductRequest) and dto.pending == 'False':
                    product_data = dict()

                    for data_field in self.PRODUCT_DATA_FIELDS:
                        data = None

                        # get data from dto
                        if getattr(dto, data_field, None) is not None:
                            data = getattr(dto, data_field)

                            # process units array data
                            if data_field == 'unit_conversions':  # unit_conversions
                                unit_conversions = []
                                for unit_conversion in data:  # type:CreatingShopProductUnitConversionRequest
                                    unit_conversions.append({
                                        'unit': unit_conversion.unit,
                                        'base_unit': unit_conversion.base_unit,
                                        'conversion_factor': unit_conversion.conversion_factor,
                                    })

                                data = unit_conversions

                            # process stocking data
                            elif data_field == 'first_inventory_stocking_for_unit_conversions':
                                stockings = []
                                for stocking in data:  # type:CreatingShopProductFirstStockingRequest
                                    stockings.append({
                                        'unit': stocking.unit,
                                        'stocking': stocking.stocking,
                                    })
                                data = stockings

                            # process suppliers data
                            elif data_field == 'suppliers':
                                suppliers = []
                                for create_supplier_request in data:  # type:CreatingShopSupplierWithPurchasePriceRequest
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
                    # product_data['title'] += ''.join(random.sample(string.ascii_lowercase, 8))
                    # product_data['sku'] += ''.join(random.sample(string.ascii_uppercase, 3))

                    product = shop.create_product(**product_data)

                # make response
                if product:
                    response_dto = AddingShopProductResponse(
                        product_id=product.product_id,
                    )
                    self._ob.present(response_dto=response_dto)

                    # increase aggregate version
                    shop.version += 1
                    uow.commit()
                else:
                    raise Exception(ExceptionMessages.CREATED_PRODUCT_FAILED)
            except IntegrityError as exc:
                raise exc
            except Exception as exc:
                raise exc
