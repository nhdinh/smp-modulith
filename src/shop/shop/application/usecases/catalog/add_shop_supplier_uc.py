#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from shop.application.services.shop_unit_of_work import ShopUnitOfWork
from shop.application.usecases.shop_uc_common import get_shop_or_raise
from shop.domain.entities.value_objects import ShopSupplierId
from web_app.serialization.dto import BaseAuthorizedShopUserRequest


@dataclass
class AddingShopSupplierRequest(BaseAuthorizedShopUserRequest):
  name: str
  contact_name: str
  contact_phone: str


@dataclass
class AddingShopSupplierResponse:
  supplier_id: ShopSupplierId


class AddingShopSupplierResponseBoundary(abc.ABC):
  @abc.abstractmethod
  def present(self, dto: AddingShopSupplierResponse):
    raise NotImplementedError


class AddShopSupplierUC:
  def __init__(self, ob: AddingShopSupplierResponseBoundary, uow: ShopUnitOfWork):
    self._ob = ob
    self._uow = uow

  def execute(self, dto: AddingShopSupplierRequest):
    with self._uow as uow:  # type:ShopUnitOfWork
      try:
        shop = get_shop_or_raise(shop_id=dto.shop_id, user_id=dto.current_user_id, uow=uow)

        # make supplier
        supplier = shop.create_supplier(
          supplier_name=dto.name,
          contact_name=dto.contact_name,
          contact_phone=dto.contact_phone
        )  # type: ShopSupplier

        # make response
        response_dto = AddingShopSupplierResponse(supplier_id=supplier.supplier_id)
        self._ob.present(response_dto)

        shop.version += 1

        uow.commit()
      except Exception as exc:
        raise exc
