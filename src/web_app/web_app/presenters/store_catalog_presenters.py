#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc

from flask import Response, make_response, jsonify

from store.application.usecases.update_store_catalog import UpdatingStoreCatalogResponseBoundary, \
    UpdatingStoreCatalogResponse
from store.application.usecases.update_store_collection_uc import UpdatingStoreCollectionResponse, \
    UpdatingStoreCollectionResponseBoundary


class AbstractResponseBoundary(abc.ABC):
    response: Response

    @abc.abstractmethod
    def _present(self, response_dto):
        raise NotImplementedError

    def present(self, response_dto) -> None:
        self.response = self._present(response_dto)


class UpdatingStoreCollectionPresenter(UpdatingStoreCollectionResponseBoundary):
    response: Response

    def present(self, response_dto: UpdatingStoreCollectionResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))


class UpdatingStoreCatalogPresenter(UpdatingStoreCatalogResponseBoundary):
    response: Response

    def present(self, response_dto: UpdatingStoreCatalogResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))
