#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import namedtuple
from datetime import datetime, date

import requests

from pricing.domain.value_objects import GenericItemStatus, ProductId, ShopId, ResourceOwner, ExceptionMessages, Price
from pricing.services.pricing_uow import PricingUnitOfWork


def get_authorize_bounded_user(user_id: str, uow: PricingUnitOfWork, **kwargs):
    try:
        user = uow.prices.get_owner(user_id=user_id)
        if not user:
            if 'create_on_failed' in kwargs.keys():
                email = kwargs['email']
                status = kwargs['user_status'] | 'NORMAL'
                user = ResourceOwner(user_id=user_id, email=email, status=GenericItemStatus(status))
                uow.prices.save_owner(user)
            else:
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


def is_duration_overlapping(start1: date, end1: date, start2: date, end2: date):
    Range = namedtuple('Range', ['start', 'end'])

    if not end1 and not end2:
        return True
    elif not end1 and end2:
        return start1 <= start2 or start1 <= end2
    elif end1 and not end2:
        return start1 >= start2 or end1 >= start2
    else:
        r1 = Range(start=start1, end=end1)
        r2 = Range(start=start2, end=end2)

        latest_start = max(r1.start, r2.start)
        earliest_end = min(r1.end, r2.end)
        delta = (earliest_end - latest_start).days + 1
        overlap = max(0, delta)

        return overlap > 0
