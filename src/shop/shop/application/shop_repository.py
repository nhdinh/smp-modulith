#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from typing import Optional

from foundation.repository import AbstractRepository

from shop.domain.entities.shop import Shop
from shop.domain.entities.shop_product import ShopProduct
from shop.domain.entities.shop_registration import ShopRegistration
from shop.domain.entities.shop_user import ShopUser, SystemUser
from shop.domain.entities.value_objects import ShopId, ShopProductId


class AbstractShopRepository(AbstractRepository):
    def save(self, shop: Shop) -> None:
        self._save(shop)

    @abc.abstractmethod
    def get(self, shop_id: ShopId) -> Shop:
        raise NotImplementedError


class SqlAlchemyShopRepository(AbstractShopRepository):
    def get(self, shop_id_to_find: ShopId) -> Optional[Shop]:
        return self._sess.query(Shop).filter(Shop.shop_id == shop_id_to_find).first()

    def get_shop_by_admin_id(self, user_id: str) -> Optional[Shop]:
        return self._sess.query(Shop) \
            .join(ShopUser, Shop._users).filter(ShopUser.user_id == user_id).first()

    def _save(self, store: Shop) -> None:
        self._sess.add(store)

    def save_registration(self, shop_registration: ShopRegistration) -> None:
        self._sess.add(shop_registration)

    def get_registration_by_token(self, token):
        return self._sess.query(ShopRegistration).filter(ShopRegistration.confirmation_token == token).first()

    def get_registration_by_email(self, email: str) -> Optional[ShopRegistration]:
        return self._sess.query(ShopRegistration).filter(ShopRegistration.owner_email == email).first()

    def get_shop_by_email(self, email: str) -> Shop:
        """
        Fetch shop by user's email
        :param email:
        """
        return self._sess.query(Shop) \
            .join(ShopUser, Shop._users) \
            .join(SystemUser, ShopUser.user_id == SystemUser.user_id).filter(SystemUser.email == email).first()

    def get_product_by_id(self, product_id: ShopProductId):
        return self._sess.query(ShopProduct).filter(ShopProduct.product_id == product_id).first()
