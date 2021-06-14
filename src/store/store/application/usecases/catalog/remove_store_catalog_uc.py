#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from typing import Optional

from store.application.services.store_unit_of_work import StoreUnitOfWork
from store.application.usecases.const import ExceptionMessages
from store.application.usecases.store_uc_common import fetch_store_by_owner


@dataclass
class RemovingStoreCatalogRequest:
    current_user: str
    catalog_reference: str
    remove_completely: Optional[bool] = False


@dataclass
class RemovingStoreCatalogResponse:
    status: bool


class RemovingStoreCatalogResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response: RemovingStoreCatalogResponse):
        raise NotImplementedError


class RemoveStoreCatalogUC:
    def __init__(self, boundary: RemovingStoreCatalogResponseBoundary, uow: StoreUnitOfWork):
        self._ob = boundary
        self._uow = uow

    def execute(self, dto: RemovingStoreCatalogRequest) -> None:
        with self._uow as uow:  # type: StoreUnitOfWork
            try:
                # get input
                remove_completely = dto.remove_completely

                # get store
                store = fetch_store_by_owner(store_owner=dto.current_user, uow=uow)

                # delete catalog
                store.delete_catalog(
                    catalog_reference=dto.catalog_reference,
                    remove_completely=remove_completely
                )

                # release the dto
                response = RemovingStoreCatalogResponse(status=True)
                self._ob.present(response)

                # commit
                uow.commit()
            except Exception as exc:
                raise exc
