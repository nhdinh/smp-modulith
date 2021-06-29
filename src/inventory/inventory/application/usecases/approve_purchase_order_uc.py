#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from inventory.application.services.inventory_unit_of_work import InventoryUnitOfWork


@dataclass
class ApprovingPurchaseOrderRequest:
    pass


@dataclass
class ApprovingPurchaseOrderResponse:
    pass


class ApprovingPurchaseOrderResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: ApprovingPurchaseOrderResponse):
        raise NotImplementedError


class ApprovePurchaseOrderUC:
    def __init__(self, boundary: ApprovingPurchaseOrderResponseBoundary, uow: InventoryUnitOfWork):
        self._ob = boundary
        self._uow = uow

    def execute(self, dto: ApprovingPurchaseOrderRequest):
        with self._uow as uow:
            try:
                ...
            except Exception as exc:
                raise exc
