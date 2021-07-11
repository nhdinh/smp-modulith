#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING

import email_validator

from inventory.domain.entities.draft_purchase_order import DraftPurchaseOrderId, DraftPurchaseOrder
from store.application.usecases.const import ThingGoneInBlackHoleError

if TYPE_CHECKING:
    from inventory.domain.entities.warehouse import Warehouse

from inventory.application.services.inventory_unit_of_work import InventoryUnitOfWork
from inventory.application.usecases.const import ExceptionMessages


def is_warehouse_disabled(warehouse):
    return warehouse.disabled


def get_warehouse_by_owner_or_raise(owner: str, uow: InventoryUnitOfWork, active_only: bool = True) -> 'Warehouse':
    try:
        email_validator.validate_email(owner)

        warehouse = uow.inventory.fetch_warehouse_of_owner(owner=owner)
        if not warehouse:
            raise Exception(ExceptionMessages.STORE_HAS_NO_WAREHOUSE)

        if active_only and is_warehouse_disabled(warehouse):
            raise Exception(ExceptionMessages.STORE_HAS_NO_WAREHOUSE)

        return warehouse
    except email_validator.EmailSyntaxError as exc:
        # TODO: Log for the attack
        raise exc
    except Exception as exc:
        raise exc


def get_draft_purchase_order_from_warehouse_or_raise(draft_purchase_order_id: DraftPurchaseOrderId,
                                                     warehouse: 'Warehouse') -> 'DraftPurchaseOrder':
    try:
        purchase_order = next(
            po for po in warehouse.draft_purchase_orders if po.purchase_order_id == draft_purchase_order_id)
        return purchase_order
    except StopIteration:
        raise ThingGoneInBlackHoleError(ExceptionMessages.DRAFT_PURCHASE_ORDER_NOT_FOUND)
