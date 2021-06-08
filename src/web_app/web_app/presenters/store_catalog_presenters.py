#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Response, make_response, jsonify

from store.application.usecases.update_store_collection_uc import UpdatingStoreCollectionResponse, \
    UpdatingStoreCollectionResponseBoundary


class UpdatingStoreCollectionPresenter(UpdatingStoreCollectionResponseBoundary):
    response: Response

    def present(self, response_dto: UpdatingStoreCollectionResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))
