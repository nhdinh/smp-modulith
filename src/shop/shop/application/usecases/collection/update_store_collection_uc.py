#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from shop.application.services.shop_unit_of_work import ShopUnitOfWork
from shop.application.usecases.shop_uc_common import get_shop_or_raise
from shop.domain.entities.value_objects import StoreCollectionId


@dataclass
class UpdatingStoreCollectionRequest:
    current_user: str
    collection_id: StoreCollectionId
    title: str
    disabled: bool


@dataclass
class UpdatingStoreCollectionResponse:
    status: bool


class UpdatingStoreCollectionResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: UpdatingStoreCollectionResponse):
        raise NotImplementedError


class UpdateStoreCollectionUC:
    def __init__(self, ob: UpdatingStoreCollectionResponseBoundary, uow: ShopUnitOfWork):
        self._ob = ob
        self._uow = uow

    def execute(self, dto: UpdatingStoreCollectionRequest):
        with self._uow as uow:  # type:ShopUnitOfWork
            try:
                store = get_shop_or_raise(store_owner=dto.current_user, uow=uow)

                # build  update data
                update_data = {
                    'display_name': dto.display_name,
                    'display_image': dto.display_image,
                    'disabled': dto.disabled,
                }

                store.update_collection(catalog_reference=dto.catalog_reference,
                                        collection_reference=dto.collection_id, update_data=update_data)

                response_dto = UpdatingStoreCollectionResponse(status=True)
                self._ob.present(response_dto=response_dto)

                uow.commit()
            except Exception as exc:
                raise exc
