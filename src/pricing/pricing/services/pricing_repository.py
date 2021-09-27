#!/usr/bin/env python
# -*- coding: utf-8 -*-

from foundation.repository import AbstractRepository

from pricing.domain.priced_item import PricedItem
from pricing.domain.value_objects import ProductId, ShopId, ResourceOwnerId


class SqlAlchemyPricingRepository(AbstractRepository):
    def _save(self, priced_item: PricedItem) -> None:
        self._sess.add(priced_item)

    def save(self, priced_item: PricedItem) -> None:
        self._save(priced_item)

    def get_priced_item(self, product_id: ProductId, shop_id: ShopId, owner_id: ResourceOwnerId) -> PricedItem:
        raise NotImplementedError

    def get_owner(self, user_id: str):
        raise NotImplementedError
