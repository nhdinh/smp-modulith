#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from datetime import date
from typing import Optional

from inventory.application.services.inventory_unit_of_work import InventoryUnitOfWork
from inventory.domain.entities.value_objects import DraftPurchaseOrderId
from shop.domain.entities.value_objects import StoreAddressId


@dataclass
class UpdatingDraftPurchaseOrderRequest:
    draft_purchase_order_id: DraftPurchaseOrderId
    due_date: Optional[date]
    note: Optional[str]
    delivery_address: Optional[StoreAddressId]


@dataclass
class UpdatingDraftPurchaseOrderResponse:
    pass


class UpdatingDraftPurchaseOrderResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: UpdatingDraftPurchaseOrderResponse):
        raise NotImplementedError


class UpdateDraftPurchaseOrderUC:
    def __init__(self, boundary: UpdatingDraftPurchaseOrderResponseBoundary, uow: InventoryUnitOfWork):
        self._ob = boundary
        self._uow = uow

    def execute(self, dto: UpdatingDraftPurchaseOrderRequest):
        with self._uow as uow:
            try:
                ...
            except Exception as exc:
                raise exc
