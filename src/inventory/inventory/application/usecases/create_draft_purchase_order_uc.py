#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

import abc
from datetime import datetime

from inventory.application.services.inventory_unit_of_work import InventoryUnitOfWork
from store.application.usecases.store_uc_common import fetch_store_by_owner_or_raise


@dataclass
class CreatingDraftPurchaseOrderRequest:
    reference: PurchaseOrderReference

    current_user: str
    created_at: datetime


@dataclass
class CreatingDraftPurchaseOrderResponse:
    message: str


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
                store = fetch_store_by_owner_or_raise(store_owner=dto.current_user, uow=uow)

                response_dto = CreatingDraftPurchaseOrderResponse(
                    message='blah bloh'
                )
                self._ob.present(response_dto=response_dto)
                uow.commit()
            except Exception as exc:
                raise exc
