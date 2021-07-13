#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from typing import Optional

from store.application.services.store_unit_of_work import ShopUnitOfWork
from store.application.usecases.store_uc_common import get_shop_or_raise
from store.domain.entities.value_objects import StoreCatalogId


@dataclass
class UpdatingStoreCatalogRequest:
    current_user: str
    catalog_id: StoreCatalogId
    title: Optional[str]
    disabled: Optional[bool]
    image: Optional[str]


@dataclass
class UpdatingStoreCatalogResponse:
    status: bool


class UpdatingStoreCatalogResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: UpdatingStoreCatalogResponse):
        raise NotImplementedError


class UpdateStoreCatalogUC:
    def __init__(self, ob: UpdatingStoreCatalogResponseBoundary, uow: ShopUnitOfWork):
        self._ob = ob
        self._uow = uow

    def execute(self, dto: UpdatingStoreCatalogRequest):
        with self._uow as uow:  # type:ShopUnitOfWork
            try:
                # get store
                store = get_shop_or_raise(store_owner=dto.current_user, uow=uow)

                # make update input data
                update_data = {}

                # update display_name
                if dto.title:
                    update_data['title'] = dto.title

                # toggle the catalog
                if dto.disabled is not None:
                    update_data['disabled'] = dto.disabled

                # update display_image
                if dto.image:
                    update_data['image'] = dto.image

                # do update
                store.update_catalog(catalog_id=dto.catalog_id, **update_data)

                # build the output
                response_dto = UpdatingStoreCatalogResponse(status=True)
                self._ob.present(response_dto=response_dto)

                # commit
                store.version += 1
                uow.commit()
            except Exception as exc:
                raise exc
