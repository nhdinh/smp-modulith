#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from identity.domain.value_objects import UserId
from shop.domain.dtos.shop_dtos import ShopAddressResponseDto, ShopInfoResponseDto
from web_app.serialization.dto import BaseAuthorizedShopUserRequest, SimpleListTypedResponse, BaseTimeLoggedRequest


@dataclass
class ListShopAddressesRequest(BaseAuthorizedShopUserRequest):
  ...


class ListShopAddressesQuery(abc.ABC):
  @abc.abstractmethod
  def query(self, dto: ListShopAddressesRequest) -> SimpleListTypedResponse[ShopAddressResponseDto]:
    raise NotImplementedError


@dataclass
class GetShopInfoRequest(BaseTimeLoggedRequest):
  current_user_id: UserId


class GetShopInfoQuery(abc.ABC):
  @abc.abstractmethod
  def query(self, dto: GetShopInfoRequest) -> SimpleListTypedResponse[ShopInfoResponseDto]:
    raise NotImplementedError
