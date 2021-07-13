#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from typing import Optional

from foundation.repository import AbstractRepository
from store.domain.entities.shop import Shop
from store.domain.entities.shop_user import ShopUser
from store.domain.entities.shop_user import ShopUser
from store.domain.entities.store_product import ShopProduct
from store.domain.entities.shop_registration import ShopRegistration
from store.domain.entities.value_objects import ShopId, ShopProductId


class AbstractShopRepository(AbstractRepository):
    def save(self, store: Shop) -> None:
        self._save(store)

    @abc.abstractmethod
    def get(self, shop_id: ShopId) -> Shop:
        raise NotImplementedError


class SqlAlchemyShopRepository(AbstractShopRepository):
    def get(self, shop_id_to_find: ShopId) -> Optional[Shop]:
        return self._sess.query(Shop).filter(Shop.shop_id == shop_id_to_find).first()

    def _save(self, store: Shop) -> None:
        self._sess.add(store)

    def save_registration(self, shop_registration: ShopRegistration) -> None:
        self._sess.add(shop_registration)

    def get_registration_by_token(self, token):
        return self._sess.query(ShopRegistration).filter(ShopRegistration.confirmation_token == token).first()

    def get_registration_by_email(self, email: str):
        return self._sess.query(ShopRegistration).filter(ShopRegistration.owner_email == email).first()

    def get_shop_by_email(self, email: str) -> Shop:
        """
        Fetch shop by user's email
        :param email:
        """
        return self._sess.query(Shop) \
            .join(ShopUser, Shop._managers) \
            .join(ShopUser, ShopUser.shop_user).filter(ShopUser.email == email).first()

    def get_product_by_id(self, product_id: ShopProductId):
        return self._sess.query(ShopProduct).filter(ShopProduct.product_id == product_id).first()

    def fetch_shop(self, shop_id: ShopId) -> Shop:
        return self._sess.query(Shop).filter(Shop.shop_id == shop_id).first()
