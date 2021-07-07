#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from sqlalchemy.engine.row import RowProxy


@dataclass
class StoreCollectionDto:
    collection_id: 'StoreCollectionId'
    title: str
    is_collection_disabled: bool

    def serialize(self):
        return self.__dict__


def _row_to_collection_dto(row: RowProxy) -> StoreCollectionDto:
    return StoreCollectionDto(
        collection_id=row.collection_id,
        title=row.title,
        is_collection_disabled=row.is_collection_disabled,
    )
