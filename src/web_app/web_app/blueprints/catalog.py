#!/usr/bin/env python
# -*- coding: utf-8 -*-

import flask_injector
import injector
from flask import Blueprint, jsonify, make_response, Response, abort, request, current_app
from flask_jwt_extended import jwt_required
from flask_login import current_user

from foundation.business_rule import BusinessRuleValidationError
from product_catalog.application.queries.product_catalog import FetchAllCatalogsQuery, FetchCatalogQuery
from product_catalog.application.usecases.create_catalog import CreatingCatalogResponseBoundary, \
    CreatingCatalogResponse, \
    CreatingCatalogRequest, CreateCatalogUC
from product_catalog.application.usecases.create_collection import CreatingCollectionRequest, CreateCollectionUC, \
    CreatingCollectionResponseBoundary, CreatingCollectionResponse
from product_catalog.application.usecases.toggle_catalog import TogglingCatalogResponseBoundary, ToggleCatalogUC
from web_app.serialization.dto import get_dto

catalog_blueprint = Blueprint('catalog_blueprint', __name__)


class CatalogAPI(injector.Module):
    @injector.provider
    @flask_injector.request
    def create_catalog_response_boundary(self) -> CreatingCatalogResponseBoundary:
        return CreatingCatalogPresenter()

    @injector.provider
    @flask_injector.request
    def toggle_catalog_response_boundary(self) -> TogglingCatalogResponseBoundary:
        return TogglingCatalogPresenter()


@catalog_blueprint.route('/')
@jwt_required()
def fetch_all_active_catalogs(query: FetchAllCatalogsQuery) -> Response:
    try:
        catalogs = query.query()
        return make_response(jsonify(catalogs)), 200  # type:ignore
    except Exception as exc:
        if current_app.debug:
            raise exc
        return make_response(jsonify({'messages': exc.args})), 400  # type: ignore


@catalog_blueprint.route('/all')
@jwt_required()
def fetch_all_catalogs(query: FetchAllCatalogsQuery) -> Response:
    try:
        catalogs = query.query(select_active_only=False)
        return make_response(jsonify(catalogs)), 200  # type:ignore
    except Exception as exc:
        if current_app.debug:
            raise exc
        return make_response(jsonify({'messages': exc.args})), 400  # type: ignore


@catalog_blueprint.route("/<string:catalog_query>", methods=['GET'])
@jwt_required()
def get_single_catalog(catalog_query: str, query: FetchCatalogQuery) -> Response:
    return make_response(jsonify(query.query(param=catalog_query)))


@catalog_blueprint.route('/', methods=['POST'])
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
@jwt_required()
def create_new_collection(catalog_query: str, create_collection_uc: CreateCollectionUC,
                          presenter: CreatingCatalogResponseBoundary) -> Response:
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


@catalog_blueprint.route('/<string:catalog_query>/toggle', methods=['POST'])
@jwt_required()
def toggle_catalog(catalog_query: str, toggle_catalog_uc: ToggleCatalogUC,
                   presenter: TogglingCatalogResponseBoundary) -> Response:
    try:
        toggle_catalog_uc.execute(catalog_query)
        return presenter.response, 200  # type: ignore
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


class TogglingCatalogPresenter(TogglingCatalogResponseBoundary):
    response: Response

    def present(self, response_dto: CreatingCatalogResponse):
        self.response = make_response(jsonify(response_dto.__dict__))
