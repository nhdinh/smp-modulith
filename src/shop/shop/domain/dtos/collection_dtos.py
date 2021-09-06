#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from sqlalchemy.engine.row import RowProxy

from shop.domain.entities.value_objects import ShopCollectionId


@dataclass
class ShopCollectionShortDto:
    collection_id: 'ShopCollectionId'
    title: str

    def serialize(self):
        return self.__dict__


@dataclass
class ShopCollectionDto(ShopCollectionShortDto):
    collection_status: str


def _row_to_collection_dto(row: RowProxy) -> ShopCollectionDto:
    return ShopCollectionDto(
        collection_id=row.collection_id,
        title=row.title,
        collection_status=row.collection_status,
    )
