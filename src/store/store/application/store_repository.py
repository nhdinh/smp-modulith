#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from typing import Optional

from foundation.repository import AbstractRepository
from store.domain.entities.shop import Shop
from store.domain.entities.shop_manager import ShopManager
from store.domain.entities.shop_user import ShopUser
from store.domain.entities.store_product import StoreProduct
from store.domain.entities.shop_registration import ShopRegistration
from store.domain.entities.value_objects import ShopId, StoreProductId


class AbstractStoreRepository(AbstractRepository):
    def save(self, store: Shop) -> None:
        self._save(store)

    @abc.abstractmethod
    def get(self, store: ShopId) -> Shop:
        raise NotImplementedError


class SqlAlchemyStoreRepository(AbstractStoreRepository):
    def get(self, store_id_to_find: ShopId) -> Optional[Shop]:
        return self._sess.query(Shop).filter(Shop.shop_id == store_id_to_find).first()

    def _save(self, store: Shop) -> None:
        self._sess.add(store)

    def save_registration(self, store_registration) -> None:
        self._sess.add(store_registration)

    def fetch_registration_by_token(self, token):
        return self._sess.query(ShopRegistration).filter(ShopRegistration.confirmation_token == token).first()

    def fetch_registration_by_registration_email(self, email: str):
        return self._sess.query(ShopRegistration).filter(ShopRegistration.owner_email == email).first()

    def fetch_store_of_owner(self, owner: str) -> Shop:
        """
        Fetch store of the owner
        :param owner:
        """
        return self._sess.query(Shop) \
            .join(ShopManager, Shop._managers) \
            .join(ShopUser, ShopManager.shop_user).filter(ShopUser.email == owner).first()

    def get_product_by_id(self, product_id: StoreProductId):
        return self._sess.query(StoreProduct).filter(StoreProduct.product_id == product_id).first()

    def fetch_shop(self, shop_id: ShopId) -> Shop:
        return self._sess.query(Shop).filter(Shop.shop_id == shop_id).first()
