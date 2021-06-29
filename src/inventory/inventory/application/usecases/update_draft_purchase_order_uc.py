#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

import abc

from inventory.application.services.inventory_unit_of_work import InventoryUnitOfWork


@dataclass
class UpdatingDraftPurchaseOrderRequest:
    pass


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
