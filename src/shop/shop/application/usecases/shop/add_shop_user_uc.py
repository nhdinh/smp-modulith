#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from shop.application.services.shop_unit_of_work import ShopUnitOfWork
from shop.application.usecases.shop_uc_common import get_shop_or_raise
from shop.domain.entities.value_objects import ShopId
from web_app.serialization.dto import BaseAuthorizedShopUserRequest


@dataclass
class AddingShopUserRequest(BaseAuthorizedShopUserRequest):
    user_id: str


@dataclass
class AddingShopUserResponse:
    shop_id: ShopId
    shop_user_id: str


class AddingShopUserResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: AddingShopUserResponse):
        raise NotImplementedError


class AddShopUserUC:
    def __init__(self, ob: AddingShopUserResponseBoundary, uow: ShopUnitOfWork):
        self._ob = ob
        self._uow = uow

    def execute(self, dto: AddingShopUserRequest) -> None:
        with self._uow as uow:  # type:ShopUnitOfWork
            try:
                shop = get_shop_or_raise(shop_id=dto.shop_id, user_id=dto.current_user_id,
                                         check_admin_rights=True, uow=uow)

                # build response
                response_dto = AddingShopUserResponse(
                    shop_id=shop.shop_id,
                    shop_user_id=dto.user_id
                )
                self._ob.present(response_dto=response_dto)

                shop.version += 1
                uow.commit()
            except Exception as exc:
                raise exc
