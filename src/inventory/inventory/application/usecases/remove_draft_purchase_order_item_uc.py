#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from inventory.application.services.inventory_unit_of_work import InventoryUnitOfWork
from inventory.application.usecases.const import ExceptionMessages
from inventory.application.usecases.inventory_uc_common import get_warehouse_by_owner_or_raise, \
    get_draft_purchase_order_from_warehouse_or_raise
from inventory.domain.entities.draft_purchase_order import DraftPurchaseOrderId
from inventory.domain.entities.warehouse import Warehouse
from store.application.usecases.const import ThingGoneInBlackHoleError
from store.domain.entities.value_objects import ShopProductId


@dataclass
class RemovingDraftPurchaseOrderItemResponse:
    status: bool


class RemovingDraftPurchaseOrderItemResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: RemovingDraftPurchaseOrderItemResponse) -> None:
        raise NotImplementedError


@dataclass
class RemovingDraftPurchaseOrderItemRequest:
    current_user: str
    purchase_order_id: DraftPurchaseOrderId
    product_id: ShopProductId
    unit: str


class RemoveDraftPurchaseOrderItemUC:
    def __init__(self, boundary: RemovingDraftPurchaseOrderItemResponseBoundary, uow: InventoryUnitOfWork):
        self._ob = boundary
        self._uow = uow

    def execute(self, dto: RemovingDraftPurchaseOrderItemRequest):
        with self._uow as uow:
            try:
                warehouse = get_warehouse_by_owner_or_raise(owner=dto.current_user, uow=uow)  # type: Warehouse
                draft_purchase_order = get_draft_purchase_order_from_warehouse_or_raise(draft_purchase_order_id=dto.purchase_order_id, warehouse=warehouse)

                # get item to remove
                try:
                    item = next(_item for _item in draft_purchase_order.items if
                                _item.product.product_id == dto.product_id and _item.unit_name.unit_name == dto.unit)
                    if item:
                        draft_purchase_order.remove_item(item)

                        response_dto = RemovingDraftPurchaseOrderItemResponse(
                            status=True
                        )
                        self._ob.present(response_dto)

                        # increase the version
                        draft_purchase_order.version += 1

                        uow.commit()
                except StopIteration:
                    raise ThingGoneInBlackHoleError(ExceptionMessages.DRAFT_PURCHASE_ORDER_ITEM_NOT_FOUND)
            except Exception as exc:
                raise exc
