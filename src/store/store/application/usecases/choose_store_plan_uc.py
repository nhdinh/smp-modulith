#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from store.application.services.store_unit_of_work import StoreUnitOfWork


@dataclass
class ChoosenStorePlanRequest:
    store_owner: str
    plan_id: str


@dataclass
class ChoosenStorePlanResponse:
    status: str
    store_id: str
    plan_id: str
    store_status: str


class ChoosenStorePlanResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: ChoosenStorePlanResponse) -> None:
        raise NotImplementedError


class ChooseStorePlanUC:
    def __init__(self, ob, uow: StoreUnitOfWork):
        self._ob = ob
        self._uow = uow

    def execute(self, dto: ChoosenStorePlanRequest):
        with self._uow as uow:  # type:StoreUnitOfWork
            """ 
            TODO: Need the following things to implemented first:
            
            1. Create table that contains plan_id
            2. Allow admin to select product into each plan
            
            3. Create following tables: Store>Catalog; Store>Product; Everything else... that replicate the products things
            4. Copy product into plan should be in the Async Side
            """

            raise NotImplementedError
