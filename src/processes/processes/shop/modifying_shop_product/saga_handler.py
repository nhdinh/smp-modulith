#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector

from foundation import Event
from foundation.locks import LockFactory
from foundation.method_dispatch import method_dispatch
from processes.repository import ProcessManagerDataRepo, new_process_id
from processes.shop.modifying_shop_product.saga import CreatingShopProductData, ShopCreatingNewProduct
from shop.domain.events import ShopProductCreatedEvent, ShopProductUpdatedEvent


class ShopCreatingNewProductHandler:
  LOCK_TIMEOUT = 30

  @injector.inject
  def __init__(self, process_manager: ShopCreatingNewProduct, repo: ProcessManagerDataRepo,
               lock_factory: LockFactory) -> None:
    self._process_manager = process_manager
    self._repo = repo
    self._lock_factory = lock_factory

  @method_dispatch
  def __call__(self, event: Event) -> None:
    raise NotImplementedError

  @__call__.register(ShopProductCreatedEvent)  # type:ignore
  def handle_shop_product_created(self, event: ShopProductCreatedEvent):
    data = CreatingShopProductData(process_id=new_process_id())
    lock_name = f"pm-lock-{data.product_id}-creating"
    self._run_process_manager(lock_name, data, event)

  @__call__.register(ShopProductUpdatedEvent)  # type: ignore
  def handle_shop_product_updated(self, event: ShopProductUpdatedEvent):
    data = CreatingShopProductData(process_id=new_process_id())
    lock_name = f'pm-lock-{data.product_id}-updating'
    self._run_process_manager(lock_name, data, event)

  def _run_process_manager(self, lock_name: str, data: CreatingShopProductData, event: Event) -> None:
    lock = self._lock_factory(lock_name, self.LOCK_TIMEOUT)

    with lock:
      self._process_manager.handle(event, data)
      self._repo.save(data.process_id, data)
