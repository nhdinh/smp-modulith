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

                # find catalog
                if not store.has_catalog_reference(dto.catalog_reference):
                    raise Exception(ExceptionMessages.STORE_CATALOG_NOT_FOUND)

                # check if the catalog to be deleted is not system
                catalog_to_deleted = store.get_catalog_by_reference(dto.catalog_reference)
                if catalog_to_deleted.system:
                    raise Exception(ExceptionMessages.SYSTEM_STORE_CATALOG_CANNOT_BE_REMOVED)

                # catalog found, do delete
                if remove_completely:
                    store.delete_catalog(catalog=catalog_to_deleted)
                    # collection dang khong xoa ma bi set null
                else:
                    store.move_catalog_content(source_reference=dto.catalog_reference, dest_reference='default')
                    store.delete_catalog(catalog=catalog_to_deleted)

                # do delete
                uow.session.delete(catalog_to_deleted)

                # release the dto
                response = RemovingStoreCatalogResponse(status=True)
                self._ob.present(response)

                # commit
                uow.commit()
            except Exception as exc:
                raise exc
