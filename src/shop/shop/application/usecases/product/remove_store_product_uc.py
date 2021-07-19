#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass



from foundation.fs import FileSystem
from shop.application.services.shop_unit_of_work import ShopUnitOfWork


@dataclass
class RemovingStoreProductResponse:
    ...


class RemovingStoreProductResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: RemovingStoreProductResponse):
        raise NotImplementedError


class RemoveStoreProductUC:
    def __init__(self, boundary: RemovingStoreProductResponseBoundary, uow: ShopUnitOfWork, fs: FileSystem):
        self._ob = boundary
        self._uow = uow
        self._fs = fs
