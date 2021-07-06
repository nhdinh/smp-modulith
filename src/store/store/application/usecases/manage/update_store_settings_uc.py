#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from store.application.services.store_unit_of_work import StoreUnitOfWork
from store.application.usecases.store_uc_common import get_store_by_owner_or_raise
from store.domain.entities.store import Store


@dataclass
class UpdatingStoreSettingsRequest:
    current_user: str

    key: str
    value: str


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
                store = get_store_by_owner_or_raise(store_owner=input_dto.current_user, uow=uow)  # type:Store

                if store.has_setting(key=input_dto.key):
                    store.update_setting(key=input_dto.key, value=input_dto.value)
                else:
                    raise Exception('Setting name not existed.')

                response = UpdatingStoreSettingsResponse(
                    store_id=store.store_id,
                    status=True
                )
                self._output_boundary.present(response)

                store.version += 1
                uow.commit()
            except Exception as exc:
                raise exc
