#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from typing import Optional

from store.application.services.store_unit_of_work import StoreUnitOfWork
from store.application.usecases.store_uc_common import fetch_store_by_owner
from store.domain.entities.value_objects import StoreCatalogReference, StoreCollectionReference
from store.domain.entities.value_objects import StoreId


@dataclass
class UpdatingStoreCollectionRequest:
    current_user: str
    catalog_reference: StoreCatalogReference
    collection_reference: StoreCollectionReference
    display_name: str
    disabled: bool
    display_image: Optional[str] = ''


@dataclass
class UpdatingStoreCollectionResponse:
    status: bool


class UpdatingStoreCollectionResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: UpdatingStoreCollectionResponse):
        raise NotImplementedError


class UpdateStoreCollectionUC:
    def __init__(self, ob: UpdatingStoreCollectionResponseBoundary, uow: StoreUnitOfWork):
        self._ob = ob
        self._uow = uow

    def execute(self, dto: UpdatingStoreCollectionRequest):
        with self._uow as uow:  # type:StoreUnitOfWork
            try:
                store = fetch_store_by_owner(store_owner=dto.current_user, uow=uow)

                # build  update data
                update_data = {
                    'display_name': dto.display_name,
                    'display_image': dto.display_image,
                    'disabled': dto.disabled,
                }

                store.update_collection(catalog_reference=dto.catalog_reference,
                                        collection_reference=dto.collection_reference, update_data=update_data)

                response_dto = UpdatingStoreCollectionResponse(status=True)
                self._ob.present(response_dto=response_dto)

                uow.commit()
            except Exception as exc:
                raise exc
