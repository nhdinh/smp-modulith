#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import datetime
from typing import List, Union

from sqlalchemy.engine.row import RowProxy

from db_infrastructure import GUID
from store.application.queries.dtos.store_collection_dto import StoreCollectionDto, _row_to_collection_dto
from store.domain.entities.value_objects import StoreCatalogId


@dataclass
class StoreCatalogResponseCompactedDto:
    catalog_id: StoreCatalogId
    catalog_title: str
    catalog_image: str
    is_catalog_disabled: bool

    def serialize(self):
        return self.__dict__


@dataclass
class StoreCatalogResponseDto(StoreCatalogResponseCompactedDto):
    is_default_catalog: bool
    created_at: datetime
    updated_at: datetime
    collections: List[StoreCollectionDto]


def _row_to_catalog_dto(
        row: RowProxy, collections: List[RowProxy], compacted: bool = True
) -> Union[StoreCatalogResponseCompactedDto, StoreCatalogResponseDto]:
    if compacted:
        return StoreCatalogResponseCompactedDto(
            catalog_id=row.catalog_id,
            catalog_title=row.catalog_title,
            catalog_image=row.catalog_image,
            is_catalog_disabled=row.is_catalog_disabled,
        )
    else:
        return StoreCatalogResponseDto(
            catalog_id=row.catalog_id,
            catalog_title=row.catalog_title,
            catalog_image=row.catalog_image,
            is_default_catalog=row.is_default_catalog,
            is_catalog_disabled=row.is_catalog_disabled,
            created_at=row.created_at,
            updated_at=row.updated_at,
            collections=[
                _row_to_collection_dto(collection_row) for collection_row in collections
            ],
        )
