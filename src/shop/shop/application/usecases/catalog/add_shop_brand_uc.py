#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from typing import Optional

from shop.application.services.shop_unit_of_work import ShopUnitOfWork
from shop.application.usecases.shop_uc_common import get_shop_or_raise
from shop.domain.entities.value_objects import ShopBrandId
from web_app.serialization.dto import BaseAuthorizedShopUserRequest


@dataclass
class AddingShopBrandRequest(BaseAuthorizedShopUserRequest):
  name: str
  logo: Optional[str] = ''


@dataclass
class AddingShopBrandResponse:
  brand_id: ShopBrandId


class AddingShopBrandResponseBoundary(abc.ABC):
  @abc.abstractmethod
  def present(self, response_dto: AddingShopBrandResponse):
    raise NotImplementedError


class AddShopBrandUC:
  def __init__(self, boundary: AddingShopBrandResponseBoundary, uow: ShopUnitOfWork):
    self._ob = boundary
    self._uow = uow

  def execute(self, dto: AddingShopBrandRequest) -> None:
    with self._uow as uow:  # type: ShopUnitOfWork
      try:
        shop = get_shop_or_raise(shop_id=dto.shop_id, user_id=dto.current_user_id, uow=uow)

        brand = shop.create_brand(name=dto.name, logo=dto.logo)

        response_dto = AddingShopBrandResponse(brand_id=brand.brand_id)
        self._ob.present(response_dto=response_dto)

        shop.version += 1
        uow.commit()
      except Exception as exc:
        raise exc
