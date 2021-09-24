#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from typing import List

from foundation import EventMixin
from promotion.domain.value_objects import (PromotionId, PromotionStatus, PromotionTypes)


class Promotion(EventMixin):
    def __init__(self,
                 promotion_id: PromotionId, shop_id: str, title: str, status: PromotionStatus,
                 version: int = 0) -> None:
        super(Promotion, self).__init__()

        self.shop_id = shop_id
        self.title = title
        self.status = status
        self.version = version

    def create_promotion(self, title: str, products: List[Product], active_date: datetime, expire_date: datetime, promotion_type: PromotionTypes) -> 'Promotion':
        ...
