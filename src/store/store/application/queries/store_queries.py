#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from typing import List

from web_app.serialization.dto import PaginationOutputDto, AuthorizedPaginationInputDto


@dataclass
class StoreCollectionResponseDto:
    reference: str
    display_name: str


@dataclass
class StoreCatalogResponseDto:
    store_id: str
    reference: str
    display_name: str
    collections: List[StoreCollectionResponseDto]


class FetchAllStoreCatalogsQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: AuthorizedPaginationInputDto) -> PaginationOutputDto[StoreCatalogResponseDto]:
        pass
