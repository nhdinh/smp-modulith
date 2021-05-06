#!/usr/bin/env python
# -*- coding: utf-8 -*-
import flask_injector
import injector
from flask import Blueprint, jsonify, make_response, Response, abort, request
from flask_login import current_user

from product_catalog.application.uc.create_catalog import CreatingCatalogResponseBoundary, CreatingCatalogResponse, \
    CreatingCatalogRequest, CreateCatalog
from product_catalog.application.queries.product_catalog import GetAllCatalogsQuery, GetCatalogQuery
from web_app.serialization.dto import get_dto

catalog_blueprint = Blueprint('catalog_blueprint', __name__)


class ProductCatalogAPI(injector.Module):
    @injector.provider
    @flask_injector.request
    def create_catalog_response_boundary(self) -> CreatingCatalogResponseBoundary:
        return CreatingCatalogPresenter()


@catalog_blueprint.route('/')
def list_all_catalog(query: GetAllCatalogsQuery) -> Response:
    return make_response(jsonify(query.query()))


@catalog_blueprint.route("/<string:catalog_reference>", methods=['GET'])
def get_catalow(catalog_reference: str, query: GetCatalogQuery):
    return make_response(jsonify(query.query(reference=catalog_reference)))


@catalog_blueprint.route('/', methods=['POST'])
def create_new_catalog(create_catalog_uc: CreateCatalog, presenter: CreatingCatalogResponseBoundary) -> Response:
    if not current_user.is_authenticated:
        abort(403)

    dto = get_dto(request, CreatingCatalogRequest, context={})
    create_catalog_uc.execute(dto)
    return presenter.response  # type: ignore


class CreatingCatalogPresenter(CreatingCatalogResponseBoundary):
    repsonse: Response

    def present(self, response_dto: CreatingCatalogResponse):
        message = 'Catalog created'
        self.response = make_response(jsonify({'message': message}))
