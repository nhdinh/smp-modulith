#!/usr/bin/env python
# -*- coding: utf-8 -*-
import dataclasses
from dataclasses import dataclass
from datetime import datetime
from typing import List, Union, Type, TypeVar, Callable

from sqlalchemy.engine.row import RowProxy

from foundation.logger import logger
from shop.domain.dtos.collection_dtos import ShopCollectionDto, _row_to_collection_dto
from shop.domain.entities.value_objects import ShopCatalogId


@dataclass
class ShopCatalogResponseDto:
    catalog_id: ShopCatalogId
    catalog_title: str
    catalog_image: str
    is_default_catalog: bool
    created_at: datetime
    updated_at: datetime
    status: str

    # collections: List[ShopCollectionDto]

    def serialize(self):
        return self.__dict__


def _row_to_catalog_dto(row: RowProxy) -> ShopCatalogResponseDto:
    # return ShopCatalogResponseDto(
    #     catalog_id=row.catalog_id,
    #     catalog_title=row.catalog_title,
    #     catalog_image=row.catalog_image,
    #     is_default_catalog=row.is_default_catalog,
    #     status=row.catalog_status,
    #     created_at=row.created_at,
    #     updated_at=row.updated_at,
    # )
    return _build_response_dto(klass=ShopCatalogResponseDto, row=row)


T = TypeVar("T")
TDto = TypeVar("TDto")


def _build_response_dto(klass: Type, row: RowProxy):
    if not dataclasses.is_dataclass(klass):
        raise TypeError(f'{klass} is not response dto')

    fields = dataclasses.fields(klass)
    data_dict = {}

    for field in fields:
        if not hasattr(row, field.name):
            logger.warn(f'>> _build_response_dto: RowProxy not contains field {field.name}')

        data_dict[field.name] = getattr(row, field.name, None)

    # construct a response object
    response = klass(**data_dict)
    return response

def _row_proxy_to_dto(data_rows: List[RowProxy], output_dto: Type, handler: Callable):
    ...
