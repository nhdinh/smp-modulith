#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from store.application.services.store_unit_of_work import StoreUnitOfWork


@dataclass
class RegisteringStoreRequest:
    store_name: str
    username: str
    mobile: str
    email: str
    password: str


@dataclass
class RegisteringStoreResponse:
    reference: str


class RegisteringStoreResponseBoundary(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def present(self, response_dto: RegisteringStoreResponse) -> None:
        raise NotImplementedError


class RegisterStoreUC:
    def __init__(self, ob: RegisteringStoreResponseBoundary, uow: StoreUnitOfWork):
        self._ob = ob
        self._uow = uow

    def execute(self, dto: RegisteringStoreRequest):
        with self._uow as uow:
            pass
