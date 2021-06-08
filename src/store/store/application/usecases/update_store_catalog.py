#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from typing import Optional

from store.application.services.store_unit_of_work import StoreUnitOfWork
from store.application.usecases.const import ExceptionMessages
from store.domain.entities.store import Store
from store.domain.entities.store_catalog import StoreCatalog
from store.domain.entities.value_objects import StoreId, StoreCatalogReference, StoreOwnerId


@dataclass
class UpdatingStoreCatalogRequest:
    store_id: StoreId
    current_user: str
    catalog_reference: StoreCatalogReference
    display_name: Optional[str]
    disabled: Optional[bool]
    display_image: Optional[str]


@dataclass
class TogglingStoreCatalogRequest:
    store_id: StoreId
    current_user: str
    catalog_reference: StoreCatalogReference


@dataclass
class UpdatingStoreCatalogResponse:
    store_id: StoreId
    catalog_reference: StoreCatalogReference
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
                # fetch store data by id ID
                store = self.__class__.fetch_store_by_id(store_id=input_dto.store_id, uow=uow)
                if store is None:
                    raise Exception(ExceptionMessages.STORE_NOT_FOUND)

                # if the Store is disabled by admin
                if getattr(store, 'disabled', False):
                    raise Exception(ExceptionMessages.STORE_NOT_AVAILABLE)

                if not self.validate_store_ownership(store=store, owner_email=input_dto.current_user):
                    raise Exception(ExceptionMessages.CURRENT_USER_DO_NOT_HAVE_PERMISSION_ON_STORE)

                # check catalog
                if not store.has_catalog(catalog_reference=input_dto.catalog_reference):
                    raise Exception(ExceptionMessages.CATALOG_NOT_FOUND)

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
                store.update_catalog_data(catalog_reference=input_dto.catalog_reference, update_data=update_data)

                # build the output
                response_dto = UpdatingStoreCatalogResponse(
                    store_id=store.store_id,
                    catalog_reference=input_dto.catalog_reference,
                    status=True
                )
                self._ob.present(response_dto=response_dto)

                # commit
                uow.commit()
            except Exception as exc:
                raise exc

    @classmethod
    def fetch_store_by_id(cls, store_id: StoreId, uow: StoreUnitOfWork) -> Optional[Store]:
        """
        Fetch the store from persisted database by its store_id. Return None if failed

        :param store_id: the id of store to fetch
        :param uow: Current activated UnitOfWork

        :return: Store instance or None
        """
        store = uow.stores.get(store_id_to_find=store_id)
        if not store:
            return None

        return store

    @classmethod
    def validate_store_ownership(cls, store: Store, owner_email: str) -> bool:
        """
        Validate if the store owner has the specified email
        
        :param store: ID of the store to check
        :param owner_email: email of the owner
        :return:
        """
        return store.owner.email == owner_email


class ToggleStoreCatalogUC(UpdateStoreCatalogUC):
    def execute(self, input_dto: TogglingStoreCatalogRequest):
        pass
