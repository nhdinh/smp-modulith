#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc

from flask import Response, jsonify, make_response

from shop.application.usecases.catalog.add_shop_catalog_uc import (
    AddingShopCatalogResponse,
    AddingShopCatalogResponseBoundary,
)
from shop.application.usecases.catalog.add_shop_collection_uc import AddingShopCollectionResponseBoundary, \
    AddingShopCollectionResponse
from shop.application.usecases.catalog.remove_shop_catalog_uc import (
    RemovingShopCatalogResponse,
    RemovingShopCatalogResponseBoundary,
)
from shop.application.usecases.catalog.set_shop_catalogs_status_uc import SettingShopCatalogsStatusResponse, \
    SettingShopCatalogsStatusResponseBoundary
from shop.application.usecases.catalog.update_shop_catalog_uc import (
    UpdatingShopCatalogResponse,
    UpdatingShopCatalogResponseBoundary,
)
from shop.application.usecases.collection.update_store_collection_uc import (
    UpdatingStoreCollectionResponse,
    UpdatingStoreCollectionResponseBoundary,
)
from shop.application.usecases.initialize.initialize_store_with_plan_uc import (
    InitializingStoreWithPlanResponse,
    InitializingStoreWithPlanResponseBoundary,
)
from shop.application.usecases.shop_uc_common import GenericShopActionResponse, GenericShopResponseBoundary


class AbstractResponseBoundary(abc.ABC):
    response: Response

    @abc.abstractmethod
    def _present(self, response_dto):
        raise NotImplementedError

    def present(self, response_dto) -> None:
        self.response = self._present(response_dto)


class GenericStoreResponsePresenter(GenericShopResponseBoundary):
    response: Response

    def present(self, dto: GenericShopActionResponse) -> None:
        self.response = make_response(jsonify(dto.__dict__))


class AddingShopCatalogPresenter(AddingShopCatalogResponseBoundary):
    response: Response

    def present(self, dto: AddingShopCatalogResponse) -> None:
        self.response = make_response(jsonify(dto.__dict__))


class UpdatingShopCatalogPresenter(UpdatingShopCatalogResponseBoundary):
    response: Response

    def present(self, response_dto: UpdatingShopCatalogResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))


class RemovingShopCatalogPresenter(RemovingShopCatalogResponseBoundary):
    response: Response

    def present(self, response_dto: RemovingShopCatalogResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))


class AddingShopCollectionPresenter(AddingShopCollectionResponseBoundary):
    response: Response

    def present(self, response_dto: AddingShopCollectionResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))


class SettingShopCatalogsStatusPresenter(SettingShopCatalogsStatusResponseBoundary):
    response: Response

    def present(self, response_dto: SettingShopCatalogsStatusResponse):
        self.response = make_response(jsonify(response_dto.__dict__))


class UpdatingStoreCollectionPresenter(UpdatingStoreCollectionResponseBoundary):
    response: Response

    def present(self, response_dto: UpdatingStoreCollectionResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))


class InitializingStoreWithPlanResponsePresenter(InitializingStoreWithPlanResponseBoundary):
    response: Response

    def present(self, response_dto: InitializingStoreWithPlanResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))
