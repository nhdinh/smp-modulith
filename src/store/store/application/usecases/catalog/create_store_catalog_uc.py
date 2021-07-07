#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from store.application.services.store_unit_of_work import StoreUnitOfWork
from store.application.usecases.const import ExceptionMessages
from store.application.usecases.store_uc_common import get_store_by_owner_or_raise, GenericStoreActionResponse


@dataclass
class CreatingStoreCatalogRequest:
    current_user: str
    title: str
    enable_default_collection: bool = True


class CreatingStoreCatalogResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, dto: GenericStoreActionResponse):
        raise NotImplementedError


class CreateStoreCatalogUC:
    def __init__(self, ob: CreatingStoreCatalogResponseBoundary, uow: StoreUnitOfWork):
        self._ob = ob
        self._uow = uow

    def execute(self, dto: CreatingStoreCatalogRequest):
        with self._uow as uow:  # type:StoreUnitOfWork
            try:
                store = get_store_by_owner_or_raise(store_owner=dto.current_user, uow=uow)

                if store.is_catalog_exists(title=dto.title):
                    raise Exception(ExceptionMessages.STORE_CATALOG_EXISTED)

                # make catalog
                catalog = store.create_catalog(
                    title=dto.title,
                )

                store.catalogs.add(catalog)

                # make response
                response_dto = GenericStoreActionResponse(status=True)
                self._ob.present(response_dto)

                store.version += 1

                uow.commit()
            except Exception as exc:
                raise exc
