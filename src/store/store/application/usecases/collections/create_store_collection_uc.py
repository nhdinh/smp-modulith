#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from typing import Optional

from slugify import slugify

from store.application.services.store_unit_of_work import StoreUnitOfWork
from store.application.usecases.store_uc_common import fetch_store_by_owner, fetch_catalog_from_store
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
                store = fetch_store_by_owner(store_owner=dto.current_user, uow=uow)  # type:Store

                # validate collection reference
                reference = dto.reference if dto.reference else slugify(dto.display_name)

                # make collection
                collection = store.make_children_collection(of_catalog=dto.catalog_reference,
                                                            display_name=dto.display_name,
                                                            reference=reference)

                # make response
                respose_dto = CreatingStoreCollectionResponse(store_id=store.store_id,
                                                              catalog_reference=dto.catalog_reference,
                                                              collection_id=collection.collection_id,
                                                              reference=collection.reference)
                self._ob.present(response_dto=respose_dto)

                # commit
                uow.commit()
            except Exception as exc:
                raise exc
