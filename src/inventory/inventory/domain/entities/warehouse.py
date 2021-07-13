#!/usr/bin/env python
# -*- coding: utf-8 -*-
import uuid
from datetime import date, datetime
from typing import NewType, Set, Union, List, Optional
from uuid import UUID

from dateutil.utils import today

from inventory.adapter.inventory_db import generate_draft_purchase_order_id
from inventory.domain.entities.purchase_order import PurchaseOrder
from store.application.usecases.const import ThingGoneInBlackHoleError
from store.domain.entities.store_product import ShopProduct
from store.domain.entities.value_objects import StoreSupplierId, StoreAddressId, ShopProductId

from foundation.events import EventMixin, Event
from inventory.application.usecases.const import ExceptionMessages
from inventory.domain.entities.draft_purchase_order import DraftPurchaseOrder, DraftPurchaseOrderId, PurchaseOrderId
from inventory.domain.entities.draft_purchase_order_item import DraftPurchaseOrderItem
from inventory.domain.entities.purchase_order_status import PurchaseOrderStatus
from inventory.domain.events.draft_purchase_order_events import DraftPurchaseOrderCreatedEvent, \
    DraftPurchasedOrderUpdatedEvent
from store.domain.entities.shop_unit import ShopProductUnit

WarehouseId = NewType('WarehouseId', tp=str)


class Warehouse(EventMixin):
    def __init__(self,
                 version: int = 0):
        super(Warehouse, self).__init__()

        self._draft_purchase_orders = set()  # type:Set[DraftPurchaseOrder]

        # those following are approved purchase orders
        self._purchase_orders = set()  # type: Set[PurchaseOrder]

        self._domain_events = []
        self.version = version

    @property
    def domain_events(self) -> List[Event]:
        return self._domain_events

    @property
    def store(self) -> 'Store':
        return self._store

    @property
    def draft_purchase_orders(self):
        return self._draft_purchase_orders

    @property
    def processing_purchase_orders(self) -> Set:
        raise NotImplementedError

    @property
    def completed_purchase_orders(self) -> Set:
        raise NotImplementedError

    def create_draft_purchase_order(
            self,
            supplier_id_or_name: Union[StoreSupplierId, str],
            delivery_address: StoreAddressId,
            note: str,
            due_date: date,
            creator: str,
            items: List = None
    ) -> DraftPurchaseOrder:
        new_guid = generate_draft_purchase_order_id()
        supplier = self.store.get_supplier(supplier_id_or_name)
        if not supplier:
            raise ThingGoneInBlackHoleError(ExceptionMessages.SUPPLIER_NOT_FOUND)

        delivery_address = self.store.get_address(delivery_address)
        if not delivery_address:
            raise ThingGoneInBlackHoleError(ExceptionMessages.ADDRESS_NOT_FOUND)

        draft = DraftPurchaseOrder(
            purchase_order_id=new_guid,
            supplier=supplier,
            delivery_address=delivery_address,
            note=note,
            due_date=due_date,
            creator=creator,
            status=PurchaseOrderStatus.DRAFT
        )

        # process items
        if items:
            for item in items:
                loaded_product = self._get_product_from_store(product_id=item['product_id'])  # type:ShopProduct
                if loaded_product is None:
                    raise ThingGoneInBlackHoleError(ExceptionMessages.PRODUCT_NOT_FOUND)
                elif supplier not in loaded_product.suppliers:
                    raise Exception(ExceptionMessages.PRODUCT_NOT_BELONGED_TO_SELECTED_SUPPLIER)

                try:
                    loaded_unit = next(
                        u for u in loaded_product.units if u.unit_name == item['unit'])  # type:ShopProductUnit
                except StopIteration:
                    raise ThingGoneInBlackHoleError(ExceptionMessages.UNIT_NOT_FOUND)

                if item['quantity'] <= 0:
                    raise ValueError(item['quantity'])

                # create item and attached to PO
                purchase_order_item = DraftPurchaseOrderItem(
                    product=loaded_product,
                    unit=loaded_unit,
                    quantity=item['quantity'],
                    description=item['description']
                )

                draft.items.add(purchase_order_item)

        # add draft purchase order into stack
        draft_po_id = self._add_draft_purchase_order(draft)

        # add event for record, notify to the owner
        if draft_po_id == new_guid:  # mean new DraftPO created
            self._record_event(DraftPurchaseOrderCreatedEvent(
                purchase_order_id=draft.purchase_order_id,
                creator=draft.creator
            ))
        else:
            # add the event
            self._record_event(DraftPurchasedOrderUpdatedEvent(
                purchase_order_id=draft_po_id,
                updated_by=draft.creator
            ))

        return draft_po_id

    def _get_product_from_store(self, product_id: ShopProductId) -> Optional[ShopProduct]:
        try:
            product = next(p for p in self.store.products if p.product_id == product_id)
            return product
        except StopIteration as exc:
            return None

    def _add_draft_purchase_order(self, draft: DraftPurchaseOrder) -> DraftPurchaseOrderId:
        try:
            existence_draft_po = next(po for po in self._draft_purchase_orders if
                                      po.supplier == draft.supplier and
                                      po.delivery_address == draft.delivery_address and
                                      po.due_date == draft.due_date)
        except StopIteration:
            existence_draft_po = None

        if existence_draft_po is not None:
            existence_draft_po.add_or_merge_items(draft.items)

            return existence_draft_po.purchase_order_id
        else:
            self._draft_purchase_orders.add(draft)

            return draft.purchase_order_id

    def _generate_purchase_order_id(self):
        new_id = generate_draft_purchase_order_id()

        # check collision
        return new_id

    def get_latest_purchase_order_date(self) -> date:
        if len(self._purchase_orders):
            latest = sorted(self._purchase_orders,
                            key=lambda x: x.approved_date, reverse=True)[0]  # sorted with latest date first
            return latest.approved_date
        else:
            if getattr(self, 'created_at') and isinstance(self.created_at, datetime):
                return self.created_at.date()
            else:
                return today()

    def add_purchase_order_to_processing(self, purchase_order: PurchaseOrder) -> PurchaseOrderId:
        """
        Add the purchase_order into processing line

        :param purchase_order: the order to added into
        :return: id of the new added purchase order, instance of PurchaseOrderId
        """
        purchase_order.purchase_order_id = self._generate_purchase_order_id()
        self._purchase_orders.add(purchase_order)

        return purchase_order.purchase_order_id
