#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from shop.application.services.shop_unit_of_work import ShopUnitOfWork
from shop.application.usecases.shop_uc_common import get_shop_or_raise
from shop.domain.entities.value_objects import ShopWarehouseId


@dataclass
class CreatingStoreWarehouseRequest:
  current_user: str
  warehouse_name: str


@dataclass
class CreatingStoreWarehouseResponse:
  warehouse_id: ShopWarehouseId


class CreatingStoreWarehouseResponseBoundary(abc.ABC):
  @abc.abstractmethod
  def present(self, response_dto: CreatingStoreWarehouseResponse):
    raise NotImplementedError


class CreateStoreWarehouseUC:
  def __init__(self, boundary: CreatingStoreWarehouseResponseBoundary, uow: ShopUnitOfWork):
    self._ob = boundary
    self._uow = uow

  def execute(self, dto: CreatingStoreWarehouseRequest):
    with self._uow as uow:  # type:ShopUnitOfWork
      try:
        store = get_shop_or_raise(store_owner=dto.current_user, uow=uow)

        new_warehouse = store.create_warehouse(warehouse_name=dto.warehouse_name)
        store.warehouses.add(new_warehouse)

        response_dto = CreatingStoreWarehouseResponse(warehouse_id=new_warehouse.warehouse_id)
        self._ob.present(response_dto=response_dto)

        store.version += 1
        uow.commit()
      except Exception as exc:
        raise exc
