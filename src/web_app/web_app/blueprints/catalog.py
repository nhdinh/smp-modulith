#!/usr/bin/env python
# -*- coding: utf-8 -*-

import flask_injector
import injector
from flask import Blueprint, jsonify, make_response, Response, abort, request, current_app
from flask_jwt_extended import jwt_required
from flask_login import current_user

from foundation.business_rule import BusinessRuleValidationError
from product_catalog.application.queries.product_catalog import GetAllCatalogsQuery, GetCatalogQuery
from product_catalog.application.usecases.create_catalog import CreatingCatalogResponseBoundary, \
    CreatingCatalogResponse, \
    CreatingCatalogRequest, CreateCatalogUC
from product_catalog.application.usecases.create_collection import CreatingCollectionRequest, CreateCollectionUC, \
    CreatingCollectionResponseBoundary, CreatingCollectionResponse
from web_app.serialization.dto import get_dto

catalog_blueprint = Blueprint('catalog_blueprint', __name__)


class CatalogAPI(injector.Module):
    @injector.provider
    @flask_injector.request
    def create_catalog_response_boundary(self) -> CreatingCatalogResponseBoundary:
        return CreatingCatalogPresenter()


@catalog_blueprint.route('/')
def list_all_catalog(query: GetAllCatalogsQuery) -> Response:
    return make_response(jsonify(query.query()))


@catalog_blueprint.route("/<string:catalog_query>", methods=['GET'])
def get_single_catalog(catalog_query: str, query: GetCatalogQuery) -> Response:
    return make_response(jsonify(query.query(param=catalog_query)))


@catalog_blueprint.route('/', methods=['POST'], strict_slashes=False)
@jwt_required()
def create_new_catalog(create_catalog_uc: CreateCatalogUC, presenter: CreatingCatalogResponseBoundary) -> Response:
    try:
        dto = get_dto(request, CreatingCatalogRequest, context={})
        create_catalog_uc.execute(dto)
        return presenter.response, 201  # type: ignore
    except BusinessRuleValidationError as exc:
        return make_response(jsonify({'message': exc.details})), 400  # type: ignore
    except Exception as exc:
        if current_app.debug:
            raise exc
        return make_response(jsonify({'messages': exc.args})), 400  # type: ignore


@catalog_blueprint.route('/<string:catalog_query>/collections', methods=['POST'])
def create_new_collection(catalog_query: str, create_collection_uc: CreateCollectionUC,
                          presenter: CreatingCatalogResponseBoundary) -> Response:
    if not current_user.is_authenticated:
        abort(403)

    try:
        dto = get_dto(request, CreatingCollectionRequest, context={
            'catalog_query': catalog_query,
            'user_id': current_user.id
        })
        create_collection_uc.execute(dto)
        return presenter.response, 201  # type:ignore
    except BusinessRuleValidationError as exc:
        return make_response(jsonify({'message': exc.details})), 400  # type: ignore
    except Exception as exc:
        if current_app.debug:
            raise exc
        return make_response(jsonify({'messages': exc.args})), 400  # type: ignore


class CreatingCatalogPresenter(CreatingCatalogResponseBoundary):
    response: Response

    def present(self, response_dto: CreatingCatalogResponse):
        self.response = make_response(jsonify(response_dto.__dict__))


class CreatingCollectionPresenter(CreatingCollectionResponseBoundary):
    response: Response

    def present(self, response_dto: CreatingCollectionResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))
