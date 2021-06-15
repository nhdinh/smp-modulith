#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from typing import Optional

from store.application.services.store_unit_of_work import StoreUnitOfWork
from store.application.usecases.store_uc_common import fetch_store_by_owner_or_raise
from store.domain.entities.value_objects import StoreCatalogReference


@dataclass
class UpdatingStoreCatalogRequest:
    current_user: str
    catalog_reference: StoreCatalogReference
    display_name: Optional[str]
    disabled: Optional[bool]
    display_image: Optional[str]


@dataclass
class UpdatingStoreCatalogResponse:
    status: bool


class UpdatingStoreCatalogResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: UpdatingStoreCatalogResponse):
        raise NotImplementedError


class UpdateStoreCatalogUC:
    def __init__(self, ob: UpdatingStoreCatalogResponseBoundary, uow: StoreUnitOfWork):
        self._ob = ob
        self._uow = uow

    def execute(self, input_dto: UpdatingStoreCatalogRequest):
        with self._uow as uow:  # type:StoreUnitOfWork
            try:
                # get store
                store = fetch_store_by_owner_or_raise(store_owner=input_dto.current_user, uow=uow)

                # make update input data
                update_data = {}

                # update display_name
                if input_dto.display_name:
                    update_data['display_name'] = input_dto.display_name

                # toggle the catalog
                if input_dto.disabled is not None:
                    update_data['disabled'] = input_dto.disabled

                # update display_image
                if input_dto.display_image:
                    update_data['display_image'] = input_dto.display_image

                # do update
                store.update_catalog(catalog_reference=input_dto.catalog_reference, update_data=update_data)

                # build the output
                response_dto = UpdatingStoreCatalogResponse(
                    status=True
                )
                self._ob.present(response_dto=response_dto)

                # commit
                uow.commit()
            except Exception as exc:
                raise exc
