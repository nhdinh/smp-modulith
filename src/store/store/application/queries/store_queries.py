#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc

from web_app.serialization.dto import PaginationInputDto, PaginationOutputDto

total_pages: int


class FetchAllStoreCatalogsQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: PaginationInputDto) -> PaginationOutputDto:
        pass
