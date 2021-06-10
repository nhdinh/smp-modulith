#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc

from flask import Response, make_response, jsonify
from typing import NewType

from store.application.usecases.create_store_catalog_uc import CreatingStoreCatalogResponseBoundary, \
    CreatingStoreCatalogResponse
from store.application.usecases.initialize_store_with_plan_uc import InitializingStoreWithPlanResponse
from store.application.usecases.update_store_catalog_uc import UpdatingStoreCatalogResponseBoundary, \
    UpdatingStoreCatalogResponse
from store.application.usecases.update_store_collection_uc import UpdatingStoreCollectionResponse, \
    UpdatingStoreCollectionResponseBoundary


# TypedResponseBoundary = NewType('TypeResponseBoundary')


class AbstractResponseBoundary(abc.ABC):
    response: Response

    @abc.abstractmethod
    def _present(self, response_dto):
        raise NotImplementedError

    def present(self, response_dto) -> None:
        self.response = self._present(response_dto)


class CreatingStoreCatalogPresenter(CreatingStoreCatalogResponseBoundary):
    response: Response

    def present(self, dto: CreatingStoreCatalogResponse) -> None:
        self.response = make_response(jsonify(dto.__dict__))


class UpdatingStoreCatalogPresenter(UpdatingStoreCatalogResponseBoundary):
    response: Response

    def present(self, response_dto: UpdatingStoreCatalogResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))


class UpdatingStoreCollectionPresenter(UpdatingStoreCollectionResponseBoundary):
    response: Response

    def present(self, response_dto: UpdatingStoreCollectionResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))


class InitializingStoreWithPlanResponsePresenter:
    response: Response

    def present(self, response_dto: InitializingStoreWithPlanResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))
