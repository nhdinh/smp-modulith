#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from datetime import date

from typing import List

from store.application.queries.store_queries import StoreAddressResponseDto, StoreSupplierResponseDto
from web_app.serialization.dto import AuthorizedPaginationInputDto, PaginationOutputDto


@dataclass
class ProductBalanceResponseDto:
    ...


class ListProductsBalanceQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: AuthorizedPaginationInputDto) -> PaginationOutputDto[ProductBalanceResponseDto]:
        pass


@dataclass
class PurchaseOrderItemResponseDto:
    product_id: str
    unit: str
    quantity: int

    def serialize(self):
        return self.__dict__


@dataclass
class DraftPurchaseOrderResponseDto:
    purchase_order_id: str
    supplier: StoreSupplierResponseDto
    delivery_address: StoreAddressResponseDto
    creator: str
    due_date: date
    items: List[PurchaseOrderItemResponseDto]
    note: str

    def serialize(self):
        return self.__dict__


class ListDraftPurchaseOrdersQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: AuthorizedPaginationInputDto) -> PaginationOutputDto[DraftPurchaseOrderResponseDto]:
        pass
