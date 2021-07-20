#!/usr/bin/env python
# -*- coding: utf-8 -*-
from foundation.business_rule import BusinessRuleBase

from inventory.domain.entities.value_objects import PurchaseOrderStatus


class DraftPurchaseOrderMustBeUnconfirmedStatusRule(BusinessRuleBase):
    def __init__(self, purchase_order_status: PurchaseOrderStatus):
        super(DraftPurchaseOrderMustBeUnconfirmedStatusRule, self).__init__(message=self.__class__.__name__)

        self.purchase_order_status = purchase_order_status

    def is_broken(self) -> bool:
        return self.purchase_order_status != PurchaseOrderStatus.DRAFT
