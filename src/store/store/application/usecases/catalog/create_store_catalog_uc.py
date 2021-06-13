#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from typing import Optional

from slugify import slugify

from store.application.services.store_unit_of_work import StoreUnitOfWork
from store.application.usecases.const import ExceptionMessages
from store.application.usecases.store_uc_common import fetch_store_by_owner
from store.domain.entities.store import Store
from store.domain.entities.value_objects import StoreCatalogReference, StoreCatalogId


@dataclass
class CreatingStoreCatalogRequest:
    current_user: str
    catalog_reference: Optional[StoreCatalogReference]
    display_name: str
    enable_default_collection: bool = True


@dataclass
class CreatingStoreCatalogResponse:
    catalog_id: StoreCatalogId


class CreatingStoreCatalogResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, dto: CreatingStoreCatalogResponse):
        raise NotImplementedError


class CreateStoreCatalogUC:
    def __init__(self, ob: CreatingStoreCatalogResponseBoundary, uow: StoreUnitOfWork):
        self._ob = ob
        self._uow = uow

    def execute(self, dto: CreatingStoreCatalogRequest):
        with self._uow as uow:  # type:StoreUnitOfWork
            try:
                store = fetch_store_by_owner(store_owner=dto.current_user,uow=uow)

                if store.has_catalog_reference(dto.catalog_reference):
                    raise Exception(ExceptionMessages.STORE_CATALOG_EXISTED)

                # validate inputs
                reference = dto.catalog_reference if dto.catalog_reference else slugify(dto.display_name)

                # make catalog
                catalog = store.make_children_catalog(
                    reference=reference,
                    display_name=dto.display_name,
                )

                # make default collection
                if dto.enable_default_collection:
                    catalog.create_default_collection()

                catalog_id = store.add_catalog(catalog)

                # make response
                response_dto = CreatingStoreCatalogResponse(
                    catalog_id=catalog_id
                )
                self._ob.present(response_dto)

                uow.commit()
            except Exception as exc:
                raise exc
