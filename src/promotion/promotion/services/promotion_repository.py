#!/usr/bin/env python
# -*- coding: utf-8 -*-
from foundation.repository import AbstractRepository
from promotion.domain.promotion import Promotion


class SqlAlchemyPromotionRepository(AbstractRepository):
    def _save(self, promotion: Promotion) -> None:
        self._sess.add(promotion)

    def save(self, promotion: Promotion) -> None:
        self._save(promotion)
