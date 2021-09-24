#!/usr/bin/env python
# -*- coding: utf-8 -*-
from foundation.repository import AbstractRepository


class SqlAlchemyPromotionRepository(AbstractRepository):
    def _save(self, shop: Promotion) -> None:
        self._sess.add(promotion)

    def save(self, promotion: Promotion) -> None:
        self._save(promotion)
