#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from inventory.application.services.inventory_unit_of_work import InventoryUnitOfWork
from inventory.domain.entities.product import InventoryProductId


@dataclass
class InitializingFirstStockRequest:
    current_user: str
    product_id: InventoryProductId
    unit: str
    stock_quantity: int


@dataclass
class InitializingFirstStockResponse:
    in_stock_quantity: int


class InitializingFirstStockResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: InitializingFirstStockResponse) -> None:
        raise NotImplementedError


class InitializeFirstStockUC:
    def __init__(self, boundary: InitializingFirstStockResponseBoundary, uow: InventoryUnitOfWork):
        self._ob = boundary
        self._uow = uow

    def execute(self, dto: InitializingFirstStockRequest):
        try:
            ...
        except Exception as exc:
            raise exc
