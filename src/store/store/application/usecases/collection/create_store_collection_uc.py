#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from typing import Optional

from foundation.common_helpers import slugify
from store.application.services.store_unit_of_work import StoreUnitOfWork
from store.application.usecases.const import ExceptionMessages
from store.application.usecases.store_uc_common import fetch_store_by_owner_or_raise
from store.domain.entities.store import Store
from store.domain.entities.value_objects import StoreCatalogReference, StoreCollectionReference, StoreId, \
    StoreCollectionId


@dataclass
class CreatingStoreCollectionRequest:
    current_user: str
    catalog_reference: StoreCatalogReference
    reference: Optional[StoreCollectionReference]
    display_name: str


@dataclass
class CreatingStoreCollectionResponse:
    store_id: StoreId
    catalog_reference: StoreCatalogReference
    collection_id: StoreCollectionId
    reference: StoreCollectionReference


class CreatingStoreCollectionResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: CreatingStoreCollectionResponse):
        raise NotImplementedError


class CreateStoreCollectionUC:
    def __init__(self, boundary: CreatingStoreCollectionResponseBoundary, uow: StoreUnitOfWork):
        self._ob = boundary
        self._uow = uow

    def execute(self, dto: CreatingStoreCollectionRequest):
        with self._uow as uow:  # type:StoreUnitOfWork
            try:
                store = fetch_store_by_owner_or_raise(store_owner=dto.current_user, uow=uow)  # type:Store
                catalog = store.fetch_catalog_by_id_or_reference(search_term=dto.catalog_reference)

                if not catalog:
                    raise Exception(ExceptionMessages.STORE_CATALOG_NOT_FOUND)

                # validate collection reference
                strictly_reference_input = False
                if dto.reference is not None:
                    strictly_reference_input = True
                    reference = slugify(dto.reference)
                else:
                    reference = slugify(dto.display_name)

                # make collection
                collection = store.create_store_collection(display_name=dto.display_name,
                                                           reference=reference)

                # if the reference is not strictly input by user, then we can rename if needed
                store._add_collection_to_catalog(collection=collection, dest=catalog,
                                                 new_reference_if_duplicated=not strictly_reference_input)

                # make response
                response_dto = CreatingStoreCollectionResponse(store_id=store.store_id,
                                                               catalog_reference=dto.catalog_reference,
                                                               collection_id=collection.collection_id,
                                                               reference=collection.reference)
                self._ob.present(response_dto=response_dto)

                # increase version of aggregate
                store.version += 1

                # commit
                uow.commit()
            except Exception as exc:
                raise exc
