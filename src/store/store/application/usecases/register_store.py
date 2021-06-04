#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from store.application.services.store_unit_of_work import StoreUnitOfWork
from store.domain.entities.store_registration import StoreRegistration


@dataclass
class RegisteringStoreRequest:
    store_name: str
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
            # parse request data
            store_registration = StoreRegistration.create_registration(dto.store_name,
                                                                       dto.email,
                                                                       dto.password,
                                                                       dto.mobile)
            # create store_registration
            # create user_registration
            # save data
            pass
