#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from datetime import datetime

from store.application.services.store_unit_of_work import StoreUnitOfWork
from store.application.usecases.const import ExceptionMessages
from store.application.usecases.store_uc_common import get_shop_or_raise, GenericStoreActionResponse
from web_app.serialization.dto import BaseInputDto, BaseShopInputDto


@dataclass
class AddingShopCatalogRequest(BaseShopInputDto):
    name: str


class AddingShopCatalogResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, dto: GenericStoreActionResponse):
        raise NotImplementedError


class AddShopCatalogUC:
    def __init__(self, ob: AddingShopCatalogResponseBoundary, uow: StoreUnitOfWork):
        self._ob = ob
        self._uow = uow

    def execute(self, dto: AddingShopCatalogRequest):
        with self._uow as uow:  # type:StoreUnitOfWork
            try:
                store = get_shop_or_raise(shop_id=dto.shop_id, partner_id=dto.partner_id, uow=uow)

                if store.is_catalog_exists(title=dto.name):
                    raise Exception(ExceptionMessages.STORE_CATALOG_EXISTED)

                # make catalog
                catalog = store.create_catalog(
                    title=dto.name,
                )

                store.catalogs.add(catalog)

                # make response
                response_dto = GenericStoreActionResponse(status=True)
                self._ob.present(response_dto)

                store.version += 1

                uow.commit()
            except Exception as exc:
                raise exc
