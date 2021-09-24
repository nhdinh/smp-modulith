#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from promotion.domain.value_objects import PromotionId, PromotionTypes
from promotion.services.promotion_uow import PromotionUnitOfWork


@dataclass
class AddingProductPromotionRequest:
    pass

@dataclass
class AddingProductPromotionResponse:
    promotion_id: PromotionId
    promotion_type: PromotionTypes


class AddingProductPromotionResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response: AddingProductPromotionResponse):
        raise NotImplementedError


class AddProductPromotionUC:
    def __init__(self, boundary: AddingProductPromotionResponseBoundary, uow: PromotionUnitOfWork):
        self._ob = boundary
        self._uow = uow

    def execute(self, dto: AddingProductPromotionRequest):
        with self._uow as uow:  # type:PromotionUnitOfWork
            try:
                ...
            except Exception as exc:
                raise exc
