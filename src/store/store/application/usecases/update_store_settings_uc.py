#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from product_catalog import CatalogUnitOfWork


@dataclass
class UpdatingStoreSettingsRequest:
    addresses: []


@dataclass
class UpdatingStoreSettingsResponse:
    store_id: str
    status: bool


class UpdatingStoreSettingsResponseBoundary(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def present(self, response_dto: UpdatingStoreSettingsResponse) -> None:
        raise NotImplementedError


class UpdateStoreSettingsUC:
    def __init__(self,
                 output_boundary: UpdatingStoreSettingsResponseBoundary,
                 uow: CatalogUnitOfWork) -> None:
        self._output_boundary = output_boundary
        self._uow = uow

    def execute(self, input_dto: UpdatingStoreSettingsRequest) -> None:
        with self._uow as uow:  # type:CatalogUnitOfWork
            try:
                pass
            except Exception as exc:
                raise exc
