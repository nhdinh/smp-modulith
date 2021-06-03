#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from store.application.services.store_unit_of_work import StoreUnitOfWork
from store.domain.entities.value_objects import StoreId


@dataclass
class ConfirmingStoreRegistrationRequest:
    confirmation_token: str


@dataclass
class ConfirmingStoreRegistrationResponse:
    store_id: StoreId
    status: bool


class ConfirmingStoreRegistrationResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: ConfirmingStoreRegistrationResponse) -> None:
        raise NotImplementedError


class ConfirmStoreRegistrationUC:
    def __init__(
            self,
            ob: ConfirmingStoreRegistrationResponseBoundary,
            uow: StoreUnitOfWork
    ):
        self._ob = ob
        self._uow = uow

    def execute(self, dto: ConfirmingStoreRegistrationRequest):
        with self._uow as uow:
            pass
