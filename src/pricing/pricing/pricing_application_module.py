#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector

from pricing.services.pricing_uow import PricingUnitOfWork
from pricing.services.uc.add_item_purchase_price_uc import AddingItemPurchasePriceResponseBoundary, \
    AddItemPurchasePriceUC


class PricingApplicationModule(injector.Module):
    @injector.provider
    def add_purchase_price(self, boundary: AddingItemPurchasePriceResponseBoundary,
                           uow: PricingUnitOfWork) -> AddItemPurchasePriceUC:
        return AddItemPurchasePriceUC(boundary, uow)
