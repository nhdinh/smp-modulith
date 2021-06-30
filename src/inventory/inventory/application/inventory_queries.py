#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from web_app.serialization.dto import AuthorizedPaginationInputDto, PaginationOutputDto


@dataclass
class ProductBalanceResponseDto:
    ...


class FetchAllProductsBalanceQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: AuthorizedPaginationInputDto) -> PaginationOutputDto[ProductBalanceResponseDto]:
        pass
