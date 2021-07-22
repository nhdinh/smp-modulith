#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from shop.application.services.shop_unit_of_work import ShopUnitOfWork

@dataclass
class AddingShopBrandRequest:
    pass


@dataclass
class AddingShopBrandResponse:
    pass


class AddingShopBrandResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: AddingShopBrandResponse):


class AddShopBrandUC:
    def __init__(self, boundary: AddingShopBrandResponseBoundary, uow: ShopUnitOfWork):
        self._ob = boundary
        self._uow = uow

    def execute(self, dto: AddingShopBrandRequest) -> None:
        with self._uow as uow:  # type: ShopUnitOfWork
            try:
                ...
            except Exception as exc:
                raise exc
