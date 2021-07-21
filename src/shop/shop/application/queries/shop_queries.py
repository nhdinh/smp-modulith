#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from typing import List

from shop.domain.dtos.shop_dtos import ShopAddressResponseDto
from web_app.serialization.dto import BaseShopInputDto, ListOutputDto


@dataclass
class ListShopAddressesRequest(BaseShopInputDto):
    ...


class ListShopAddressesQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: ListShopAddressesRequest) -> ListOutputDto[ShopAddressResponseDto]:
        raise NotImplementedError
