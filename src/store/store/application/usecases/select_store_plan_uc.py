#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from store.application.services.store_unit_of_work import ShopUnitOfWork


@dataclass
class SelectingStorePlanRequest:
    store_owner: str
    plan_id: str


@dataclass
class SelectingStorePlanResponse:
    status: str
    store_id: str
    plan_id: str
    store_status: str


class SelectingStorePlanResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: SelectingStorePlanResponse) -> None:
        raise NotImplementedError


class SelectStorePlanUC:
    def __init__(self, ob, uow: ShopUnitOfWork):
        self._ob = ob
        self._uow = uow

    def execute(self, dto: SelectingStorePlanRequest):
        with self._uow as uow:  # type:ShopUnitOfWork
            """ 
            TODO: Need the following things to implemented first:
            
            1. Create table that contains plan_id
            2. Allow admin to select product into each plan
            
            3. Create following tables: Store>Catalog; Store>Product; Everything else... that replicate the products things
            4. Copy product into plan should be in the Async Side
            """

            raise NotImplementedError
