#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from store.application.services.store_unit_of_work import StoreUnitOfWork


@dataclass
class UpdatingStoreSettingsRequest:
    # addresses: []
    some_key: str


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
                 uow: StoreUnitOfWork) -> None:
        self._output_boundary = output_boundary
        self._uow = uow

    def execute(self, input_dto: UpdatingStoreSettingsRequest) -> None:
        with self._uow as uow:  # type:StoreUnitOfWork
            try:
                pass
            except Exception as exc:
                raise exc
