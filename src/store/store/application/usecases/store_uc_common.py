#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

import email_validator
from typing import Set

from sqlalchemy import select
from sqlalchemy.engine import Connection

from foundation.common_helpers import uuid_validate
from foundation.uow import SqlAlchemyUnitOfWork
from foundation.value_objects.address import LocationCountry, LocationCitySubDivision
from store.application.services.store_unit_of_work import StoreUnitOfWork
from store.application.usecases.const import ExceptionMessages, ExceptionWhileFindingThingInBlackHole
from store.domain.entities.store import Store
from store.domain.entities.store_catalog import StoreCatalog
from store.domain.entities.store_collection import StoreCollection, StoreCollectionId
from store.domain.entities.store_product import StoreProduct, StoreProductId


@dataclass
class GenericStoreActionRequest:
    current_user: str


@dataclass
class GenericStoreActionResponse:
    status: bool


class GenericStoreResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, dto: GenericStoreActionResponse):
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


def fetch_store_by_owner_or_raise(store_owner: str, uow: StoreUnitOfWork, active_only: bool = True) -> Store:
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
            raise ExceptionWhileFindingThingInBlackHole(ExceptionMessages.STORE_NOT_FOUND)

        if active_only and is_store_disabled(store):
            raise Exception(ExceptionMessages.STORE_NOT_AVAILABLE)

        return store
    except email_validator.EmailSyntaxError as exc:
        # TODO: Log for the attack
        raise exc
    except Exception as exc:
        raise exc


def fetch_catalog_from_store_or_raise(by_catalog: str, store: Store) -> StoreCatalog:
    """
    Fetch the catalog from specified store, by it reference or catalog_id

    :param by_catalog: reference or catalog_id, the catalog which is want to fetch, in str
    :param store: instance of `Store`

    :return: instance of `StoreCatalog` or raise Exception if not existed
    """
    try:
        # validate store
        if not store or getattr(store, 'store_id') is None:
            raise ExceptionWhileFindingThingInBlackHole(ExceptionMessages.STORE_NOT_FOUND)

        catalog = store.fetch_catalog_by_id_or_reference(search_term=by_catalog)

        if not catalog:
            raise ExceptionWhileFindingThingInBlackHole(ExceptionMessages.STORE_CATALOG_NOT_FOUND)

        return catalog
    except Exception as exc:
        raise exc


def fetch_collection_from_catalog_or_raise(by_collection: str, catalog: StoreCatalog) -> StoreCollection:
    try:
        # validate catalog
        if not catalog or type(catalog) is not StoreCatalog or getattr(catalog, 'catalog_id') is None:
            raise ExceptionWhileFindingThingInBlackHole(ExceptionMessages.STORE_CATALOG_NOT_FOUND)

        collection = None
        uuid = uuid_validate(by_collection)
        if uuid:
            collection = catalog.get_collection_by_id(collection_id=StoreCollectionId(uuid))
        else:
            collection = catalog.get_collection_by_reference(collection_reference=by_collection)

        if not collection:
            raise ExceptionWhileFindingThingInBlackHole(ExceptionMessages.STORE_COLLECTION_NOT_FOUND)

        return collection
    except Exception as exc:
        raise exc


def get_product_by_id_or_raise(product_id: StoreProductId, uow: StoreUnitOfWork) -> StoreProduct:
    try:
        # validate product_id
        product = uow.stores.get_product_by_id(product_id=product_id)

        if not product:
            raise ExceptionWhileFindingThingInBlackHole(ExceptionMessages.STORE_PRODUCT_NOT_FOUND)

        return product
    except Exception as exc:
        raise exc


def countries(uow: SqlAlchemyUnitOfWork) -> Set[LocationCountry]:
    try:
        query = select(LocationCountry)
        country_rows = uow._session.execute(query).all()
        return set(country_rows)
    except Exception as exc:
        raise exc


def get_location(sub_division_id: str, uow: SqlAlchemyUnitOfWork) -> LocationCitySubDivision:
    try:
        location = uow.session.query(LocationCitySubDivision).filter(
            LocationCitySubDivision.sub_division_id == sub_division_id).first()
        return location
    except Exception as exc:
        raise exc
