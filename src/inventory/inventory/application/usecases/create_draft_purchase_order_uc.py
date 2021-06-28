#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

import abc

from inventory.application.services.inventory_unit_of_work import InventoryUnitOfWork


@dataclass
class CreatingDraftPurchaseOrderRequest:
    pass


@dataclass
class CreatingDraftPurchaseOrderResponse:
    pass


class CreatingDraftPurchaseOrderResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: CreatingDraftPurchaseOrderResponse):
        raise NotImplementedError


class CreateDraftPurchaseOrderUC:
    def __init__(self, boundary: CreatingDraftPurchaseOrderResponseBoundary, uow: InventoryUnitOfWork):
        self._ob = boundary
        self._uow = uow

    def execute(self, dto: CreatingDraftPurchaseOrderRequest):
        with self._uow as uow:
            try:
                ...
            except Exception as exc:
                raise exc
