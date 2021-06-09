#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional

from store.application.services.store_unit_of_work import StoreUnitOfWork

from store.domain.entities.store import Store
from store.domain.entities.value_objects import StoreId


def fetch_store_by_id(store_id: StoreId, uow: StoreUnitOfWork) -> Optional[Store]:
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


def validate_store_ownership(store: Store, owner_email: str) -> bool:
    """
    Validate if the store owner has the specified email

    :param store: ID of the store to check
    :param owner_email: email of the owner
    :return:
    """
    return store.owner.email == owner_email
