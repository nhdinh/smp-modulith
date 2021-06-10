#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from store.application.services.store_unit_of_work import StoreUnitOfWork


@dataclass
class AddingStoreManagerRequest:
    store_owner: str
    user_email: str


@dataclass
class AddingStoreManagerResponse:
    store_id: str
    store_manager_id: str
    status: str


class AddingStoreManagerResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: AddingStoreManagerResponse):
        raise NotImplementedError


class AddStoreManagerUC:
    def __init__(self, ob: AddingStoreManagerResponseBoundary, uow: StoreUnitOfWork):
        self._ob = ob
        self._uow = uow

    def execute(self, input_dto: AddingStoreManagerRequest) -> None:
        with self._uow as uow:  # type:StoreUnitOfWork
            raise NotImplementedError
