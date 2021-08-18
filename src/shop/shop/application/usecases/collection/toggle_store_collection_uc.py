#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from shop.application.services.shop_unit_of_work import ShopUnitOfWork
from shop.application.usecases.collection.update_store_collection_uc import UpdatingStoreCollectionResponseBoundary
from shop.domain.entities.value_objects import ShopCollectionId


@dataclass
class TogglingStoreCollectionRequest:
  current_user: str
  collection_reference: ShopCollectionId


class ToggleStoreCollectionUC:
  def __init__(self, boundary: UpdatingStoreCollectionResponseBoundary, uow: ShopUnitOfWork):
    self._ob = boundary
    self._uow = uow

  def execute(self, input_dto: TogglingStoreCollectionRequest):
    with self._uow as uow:  # type:ShopUnitOfWork
      try:
        raise NotImplementedError
        # get store
        store = get_shop_or_raise(store_owner=input_dto.current_user, uow=uow)

        # do update
        store.toggle_collection(catalog_reference=input_dto.catalog_reference,
                                collection_reference=input_dto.collection_reference)

        # build the output
        response_dto = UpdatingStoreCollectionResponse(
          status=True
        )
        self._ob.present(response_dto=response_dto)

        # commit
        uow.commit()
      except Exception as exc:
        raise exc
