#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from typing import Optional, Union

import email_validator

from store import StoreUnitOfWork
from store.application.usecases.const import ExceptionMessages
from store.domain.entities.store import Store
from store.domain.entities.store_catalog import StoreCatalog
from store.domain.entities.value_objects import StoreCatalogId, StoreCatalogReference


@dataclass
class GenericStoreActionRequest:
    current_user: str


@dataclass
class GenericStoreActionResponse:
    status: bool


class GenericStoreResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, generic_dto: GenericStoreActionResponse):
        raise NotImplementedError


def validate_store_ownership(store: Store, owner_email: str) -> bool:
    """
    Validate if the store owner has the specified email

    :param store: ID of the store to check
    :param owner_email: email of the owner
    :return:
    """
    return store.owner.email == owner_email


def is_store_disabled(store: Store) -> bool:
    """
    Indicate if the store is disabled or not

    :param store: the `Store` to check
    :return: disabled or not
    """
    return getattr(store, 'disabled', False)


def fetch_store_by_owner(store_owner: str, uow: StoreUnitOfWork, active_only: bool = True) -> Store:
    """
    Fetch store information from persisted data by its owner's email

    :param store_owner: email of the store owner
    :param uow: injected StoreUnitOfWork
    :param active_only: Search for active store only (the inactive store means that the store was disabled by admins)
    :return: instance of `Store` or None
    """
    # validate input
    try:
        email_validator.validate_email(store_owner)

        store = uow.stores.fetch_store_of_owner(owner=store_owner)
        if not store:
            raise Exception(ExceptionMessages.STORE_NOT_FOUND)

        if active_only and is_store_disabled(store):
            raise Exception(ExceptionMessages.STORE_NOT_AVAILABLE)

        return store
    except email_validator.EmailSyntaxError as exc:
        # TODO: Log for the attack
        raise exc
    except Exception as exc:
        raise exc


def fetch_catalog_from_store(
        by_catalog: Union[StoreCatalogId, StoreCatalogReference],
        store: Store
) -> StoreCatalog:
    try:
        # validate store
        if not store or getattr(store, 'store_id') is None:
            raise Exception(ExceptionMessages.STORE_NOT_FOUND)

        catalog = None
        if type(by_catalog) is str:
            catalog = store.get_catalog_by_reference(catalog_reference=by_catalog)
        elif type(by_catalog) is StoreCatalogId:
            catalog = store.get_catalog_by_id(catalog_id=by_catalog)

        if not catalog:
            raise Exception(ExceptionMessages.STORE_CATALOG_NOT_FOUND)

        return catalog
    except Exception as exc:
        raise exc
