#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from foundation.fs import FileSystem
from shop.application.services.shop_unit_of_work import ShopUnitOfWork


@dataclass
class RemovingShopProductsResponse:
  ...


class RemovingShopProductsResponseBoundary(abc.ABC):
  @abc.abstractmethod
  def present(self, response_dto: RemovingShopProductsResponse):
    raise NotImplementedError


class RemoveShopProducstUC:
  def __init__(self, boundary: RemovingShopProductsResponseBoundary, uow: ShopUnitOfWork, fs: FileSystem):
    self._ob = boundary
    self._uow = uow
    self._fs = fs
