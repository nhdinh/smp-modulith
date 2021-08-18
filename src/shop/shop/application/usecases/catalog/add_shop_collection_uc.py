#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from typing import Optional

from shop.application.services.shop_unit_of_work import ShopUnitOfWork
from shop.application.usecases.shop_uc_common import (
  get_catalog_from_shop_or_raise,
  get_shop_or_raise,
)
from shop.domain.entities.shop_collection import ShopCollection
from shop.domain.entities.value_objects import ShopCatalogId, ExceptionMessages, ShopCollectionId
from web_app.serialization.dto import BaseAuthorizedShopUserRequest


@dataclass
class AddingShopCollectionRequest(BaseAuthorizedShopUserRequest):
  catalog_id: ShopCatalogId
  title: str
  image: Optional[str]


@dataclass
class AddingShopCollectionResponse:
  collection_id: ShopCollectionId


class AddingShopCollectionResponseBoundary(abc.ABC):
  @abc.abstractmethod
  def present(self, response_dto: AddingShopCollectionResponse):
    raise NotImplementedError


class AddShopCollectionUC:
  def __init__(self, boundary: AddingShopCollectionResponseBoundary, uow: ShopUnitOfWork):
    self._ob = boundary
    self._uow = uow

  def execute(self, dto: AddingShopCollectionRequest):
    with self._uow as uow:  # type:ShopUnitOfWork
      try:
        shop = get_shop_or_raise(shop_id=dto.shop_id, user_id=dto.current_user_id, uow=uow)
        catalog = get_catalog_from_shop_or_raise(catalog_id=dto.catalog_id, shop=shop)

        if catalog.is_collection_exists(collection_title=dto.title):
          raise Exception(ExceptionMessages.SHOP_COLLECTION_EXISTED)

        # make collection
        collection = shop.make_collection(title=dto.title, parent_catalog=catalog)  # type:ShopCollection

        # make response
        response_dto = AddingShopCollectionResponse(
          collection_id=collection.collection_id
        )
        self._ob.present(response_dto=response_dto)

        # increase version of aggregate
        shop.version += 1

        # commit
        uow.commit()
      except Exception as exc:
        raise exc
