#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pricing.domain.value_objects import GenericItemStatus, ProductId, ShopId, ResourceOwner, ExceptionMessages
from pricing.services.pricing_uow import PricingUnitOfWork


def get_authorize_bounded_user(user_id: str, uow: PricingUnitOfWork):
    try:
        user = uow.prices.get_owner(user_id=user_id)
        if not user:
            raise Exception(ExceptionMessages.RESOURCE_OWNER_NOT_FOUND)

        if user.status != GenericItemStatus.NORMAL:
            raise Exception(ExceptionMessages.URESOURCE_OWNER_NOT_ACTIVE)

        return user
    except Exception as exc:
        raise exc


def get_priced_item(owner: ResourceOwner, shop_id: ShopId, product_id: ProductId, uow: PricingUnitOfWork):
    try:
        priced_item = uow.prices.get_priced_item(product_id=product_id, shop_id=shop_id, owner_id=owner.user_id)
        if not priced_item:
            raise Exception(ExceptionMessages.PRICED_ITEM_NOT_FOUND)

        if priced_item.status != GenericItemStatus.NORMAL:
            raise Exception(ExceptionMessages.PRICED_ITEM_NOT_ACTIVE)

        return priced_item
    except Exception as exc:
        raise exc
