#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

import email_validator

from foundation.events import ThingGoneInBlackHoleError
from shop.application.services.shop_unit_of_work import ShopUnitOfWork
from shop.domain.entities.shop import Shop
from shop.domain.entities.shop_catalog import ShopCatalog
from shop.domain.entities.shop_collection import ShopCollection
from shop.domain.entities.shop_product import ShopProduct
from shop.domain.entities.value_objects import ExceptionMessages, ShopCatalogId, ShopCollectionId, ShopId, ShopProductId


@dataclass
class GenericShopActionRequest:
    current_user: str


@dataclass
class GenericShopActionResponse:
    status: bool


class GenericShopResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, dto: GenericShopActionResponse):
        raise NotImplementedError


def validate_shop(shop: Shop, owner_email: str) -> bool:
    """
    Validate if the store owner has the specified email

    :param shop: ID of the store to check
    :param owner_email: email of the owner
    :return:
    """
    return shop.owner.email == owner_email


def is_store_disabled(store: Shop) -> bool:
    """
    Indicate if the store is disabled or not

    :param store: the `Store` to check
    :return: disabled or not
    """
    return getattr(store, 'disabled', False)


def get_shop_or_raise(shop_id: ShopId,
                      partner_id: str,
                      uow: ShopUnitOfWork,
                      active_only: bool = True) -> Shop:
    """
    Fetch store information from persisted data by its owner's email

    :param shop_id:
    :param partner_id:
    :param uow: injected StoreUnitOfWork
    :param active_only: Search for active store only (the inactive store means that the store was disabled by admins)
    :return: instance of `Shop` or None
    """
    # validate input
    try:
        shop = uow.shops.get(shop_id_to_find=shop_id)
        if not shop:
            raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_NOT_FOUND)

        try:
            manager = next(m for m in shop.users if m.user_id == partner_id)
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


def get_catalog_from_shop_or_raise(catalog_id: ShopCatalogId, shop: Shop) -> ShopCatalog:
    """
    Fetch the catalog from specified shop, by it reference or catalog_id

    :param catalog_id: reference or catalog_id, the catalog which is want to fetch, in str
    :param shop: instance of `Shop`

    :return: instance of `ShopCatalog` or raise Exception if not existed
    """

    if not shop or getattr(shop, 'shop_id') is None:
        raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_NOT_FOUND)

    # catalog = store.fetch_catalog_by_id_or_reference(search_term=catalog_id)
    try:
        catalog = next(c for c in shop.catalogs if c.catalog_id == catalog_id)
        return catalog
    except StopIteration:
        raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_CATALOG_NOT_FOUND)


def get_collection_from_catalog_or_raise(collection_id: ShopCollectionId, catalog: ShopCatalog) -> ShopCollection:
    try:
        # validate catalog
        if not catalog or not isinstance(catalog, ShopCatalog) or getattr(catalog, 'catalog_id') is None:
            raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_CATALOG_NOT_FOUND)

        collection = catalog.get_collection_by_id(collection_id=collection_id)

        if not collection:
            raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_COLLECTION_NOT_FOUND)

        return collection
    except Exception as exc:
        raise exc


def get_product_by_id_or_raise(product_id: ShopProductId, uow: ShopUnitOfWork) -> ShopProduct:
    try:
        # validate product_id
        product = uow.shops.get_product_by_id(product_id=product_id)

        if not product:
            raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_PRODUCT_NOT_FOUND)

        return product
    except Exception as exc:
        raise exc


"""
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
"""
