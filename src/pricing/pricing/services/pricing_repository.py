#!/usr/bin/env python
# -*- coding: utf-8 -*-

from foundation.repository import AbstractRepository

from pricing.domain.priced_item import PricedItem
from pricing.domain.value_objects import ProductId, ShopId, ResourceOwnerId, ResourceOwner


class SqlAlchemyPricingRepository(AbstractRepository):
    def _save(self, entity) -> None:
        self._sess.add(entity)

    def save(self, priced_item: PricedItem) -> None:
        self._save(priced_item)

    def save_owner(self, owner: ResourceOwner) -> None:
        self._save(owner)

    def get_priced_item(self, product_id: ProductId, shop_id: ShopId, owner_id: ResourceOwnerId) -> PricedItem:
        # return self._sess.query(PricedItem).filter_by(**{
        #     product_id: product_id,
        #     shop_id: shop_id,
        #     owner_id: owner_id
        # }).first()
        return self._sess.query(PricedItem).filter(PricedItem.product_id == product_id, PricedItem.shop_id == shop_id,
                                                   PricedItem.owner_id == owner_id).first()

    def get_owner(self, user_id: str):
        return self._sess.query(ResourceOwner).filter(ResourceOwner.user_id == user_id).first()
