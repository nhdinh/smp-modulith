#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from typing import List, Optional
from uuid import UUID


@dataclass
class CatalogDto:
    reference: str
    display_name: str
    disabled: bool


class GetAllCatalogsQuery(abc.ABC):
    @abc.abstractmethod
    def query(self) -> List[CatalogDto]:
        pass


class GetCatalogQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, param: str) -> Optional[CatalogDto]:
        pass


class GetCatalogByReferenceQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, reference: str) -> CatalogDto:
        pass
