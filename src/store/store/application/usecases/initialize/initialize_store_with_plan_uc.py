#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from uuid import UUID

from store import ShopUnitOfWork


@dataclass(unsafe_hash=True)
class InitializingStoreWithPlanResponse:
    store_id: UUID
    plan_id: UUID
    status: str


class InitializingStoreWithPlanResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, dto: InitializingStoreWithPlanResponse):
        raise NotImplementedError


@dataclass
class InitializingStoreWithPlanRequest:
    current_user: str
    plan_id: UUID


class InitializeStoreWithPlanUC:
    def __init__(self, ob: InitializingStoreWithPlanResponseBoundary, uow: ShopUnitOfWork):
        self._ob = ob
        self._uow = uow

    def execute(self, dto: InitializingStoreWithPlanRequest):
        raise NotImplementedError
