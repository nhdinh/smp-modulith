#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from identity.domain.value_objects import UserId
from shop.domain.dtos.shop_dtos import ShopAddressResponseDto, ShopInfoResponseDto
from web_app.serialization.dto import BaseShopInputDto, ListOutputDto, BaseInputDto


@dataclass
class ListShopAddressesRequest(BaseShopInputDto):
    ...


class ListShopAddressesQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: ListShopAddressesRequest) -> ListOutputDto[ShopAddressResponseDto]:
        raise NotImplementedError


@dataclass
class GetShopInfoRequest(BaseInputDto):
    partner_id: UserId


class GetShopInfoQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: GetShopInfoRequest) -> ListOutputDto[ShopInfoResponseDto]:
        raise NotImplementedError
