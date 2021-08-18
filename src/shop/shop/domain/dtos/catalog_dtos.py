#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import datetime
from typing import List, Union

from sqlalchemy.engine.row import RowProxy

from shop.domain.dtos.collection_dtos import ShopCollectionDto, _row_to_collection_dto
from shop.domain.entities.value_objects import ShopCatalogId


@dataclass
class ShopCatalogResponseCompactedDto:
  catalog_id: ShopCatalogId
  catalog_title: str
  catalog_image: str
  catalog_status: str
  is_default_catalog: bool

  def serialize(self):
    return self.__dict__


@dataclass
class ShopCatalogResponseDto(ShopCatalogResponseCompactedDto):
  created_at: datetime
  updated_at: datetime
  collections: List[ShopCollectionDto]


def _row_to_catalog_dto(
    row: RowProxy, collections: List[RowProxy], compacted: bool = True
) -> Union[ShopCatalogResponseCompactedDto, ShopCatalogResponseDto]:
  if compacted:
    return ShopCatalogResponseCompactedDto(
      catalog_id=row.catalog_id,
      catalog_title=row.catalog_title,
      catalog_image=row.catalog_image,
      catalog_status=row.catalog_status,
      is_default_catalog=row.is_default_catalog
    )
  else:
    return ShopCatalogResponseDto(
      catalog_id=row.catalog_id,
      catalog_title=row.catalog_title,
      catalog_image=row.catalog_image,
      is_default_catalog=row.is_default_catalog,
      catalog_status=row.catalog_status,
      created_at=row.created_at,
      updated_at=row.updated_at,
      collections=[
        _row_to_collection_dto(collection_row) for collection_row in collections
      ],
    )
