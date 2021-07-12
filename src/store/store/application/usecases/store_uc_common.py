#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from typing import Set

import email_validator
from sqlalchemy import select

from foundation.common_helpers import uuid_validate
from foundation.database_setup import location_country_table, location_city_sub_division_table
from foundation.uow import SqlAlchemyUnitOfWork
from foundation.value_objects.address import LocationCountry, LocationCitySubDivision, LocationCitySubDivisionId
from store.application.services.store_unit_of_work import StoreUnitOfWork
from store.application.usecases.const import ExceptionMessages, ThingGoneInBlackHoleError
from store.domain.entities.shop import Shop
from store.domain.entities.store_catalog import StoreCatalog
from store.domain.entities.store_collection import StoreCollection
from store.domain.entities.store_product import StoreProduct
from store.domain.entities.value_objects import StoreCatalogId, StoreCollectionId, StoreProductId, ShopId


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


def validate_store_ownership(store: Shop, owner_email: str) -> bool:
    """
    Validate if the store owner has the specified email

    :param store: ID of the store to check
    :param owner_email: email of the owner
    :return:
    """
    return store.owner.email == owner_email


def is_store_disabled(store: Shop) -> bool:
    """
    Indicate if the store is disabled or not

    :param store: the `Store` to check
    :return: disabled or not
    """
    return getattr(store, 'disabled', False)


def get_shop_or_raise(shop_id: ShopId,
                      partner_id: str,
                      uow: StoreUnitOfWork,
                      active_only: bool = True) -> Shop:
    """
    Fetch store information from persisted data by its owner's email

    :param shop_id:
    :param partner_id:
    :param uow: injected StoreUnitOfWork
    :param active_only: Search for active store only (the inactive store means that the store was disabled by admins)
    :return: instance of `Store` or None
    """
    # validate input
    try:
        shop = uow.shops.fetch_shop(shop_id=shop_id)
        if not shop:
            raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_NOT_FOUND)

        try:
            manager = next(m for m in shop.managers if m.user_id == partner_id)
        except StopIteration:
            raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_OWNERSHIP_NOT_FOUND)

        if active_only and is_store_disabled(shop):
            raise Exception(ExceptionMessages.SHOP_NOT_AVAILABLE)

        return shop
    except email_validator.EmailSyntaxError as exc:
        # TODO: Log for the attack
        raise exc
    except Exception as exc:
        raise exc


def get_catalog_from_store_or_raise(catalog_id: StoreCatalogId, store: Shop) -> StoreCatalog:
    """
    Fetch the catalog from specified store, by it reference or catalog_id

    :param catalog_id: reference or catalog_id, the catalog which is want to fetch, in str
    :param store: instance of `Store`

    :return: instance of `StoreCatalog` or raise Exception if not existed
    """

    if not store or getattr(store, 'store_id') is None:
        raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_NOT_FOUND)

    # catalog = store.fetch_catalog_by_id_or_reference(search_term=catalog_id)
    try:
        catalog = next(c for c in store.catalogs if c.catalog_id == catalog_id)
        return catalog
    except StopIteration:
        raise ThingGoneInBlackHoleError(ExceptionMessages.STORE_CATALOG_NOT_FOUND)


def get_collection_from_catalog_or_raise(collection_id: StoreCollectionId, catalog: StoreCatalog) -> StoreCollection:
    try:
        # validate catalog
        if not catalog or not isinstance(catalog, StoreCatalog) or getattr(catalog, 'catalog_id') is None:
            raise ThingGoneInBlackHoleError(ExceptionMessages.STORE_CATALOG_NOT_FOUND)

        collection = catalog.get_collection_by_id(collection_id=collection_id)

        if not collection:
            raise ThingGoneInBlackHoleError(ExceptionMessages.STORE_COLLECTION_NOT_FOUND)

        return collection
    except Exception as exc:
        raise exc


def get_product_by_id_or_raise(product_id: StoreProductId, uow: StoreUnitOfWork) -> StoreProduct:
    try:
        # validate product_id
        product = uow.shops.get_product_by_id(product_id=product_id)

        if not product:
            raise ThingGoneInBlackHoleError(ExceptionMessages.STORE_PRODUCT_NOT_FOUND)

        return product
    except Exception as exc:
        raise exc


def list_countries(uow: SqlAlchemyUnitOfWork) -> Set[LocationCountry]:
    try:
        query = select(LocationCountry)
        country_rows = uow._session.execute(query).all()
        return set(country_rows)
    except Exception as exc:
        raise exc


def get_location(sub_division_id: LocationCitySubDivisionId, uow: SqlAlchemyUnitOfWork) -> LocationCitySubDivision:
    # TODO: Move to foundation Repository
    try:
        location = uow.session.query(LocationCitySubDivision).filter(
            LocationCitySubDivision.sub_division_id == sub_division_id).first()
        return location
    except Exception as exc:
        raise exc
