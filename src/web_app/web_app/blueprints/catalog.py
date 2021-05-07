#!/usr/bin/env python
# -*- coding: utf-8 -*-
import flask_injector
import injector
from flask import Blueprint, jsonify, make_response, Response, abort, request
from flask_login import current_user

from product_catalog.application.uc.create_catalog import CreatingCatalogResponseBoundary, CreatingCatalogResponse, \
    CreatingCatalogRequest, CreateCatalogUC
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


@catalog_blueprint.route('/', methods=['POST'], strict_slashes=False)
def create_new_catalog(create_catalog_uc: CreateCatalogUC, presenter: CreatingCatalogResponseBoundary) -> Response:
    if not current_user.is_authenticated:
        abort(403)

    try:
        dto = get_dto(request, CreatingCatalogRequest, context={})
        create_catalog_uc.execute(dto)
        return presenter.response, 201  # type: ignore
    except Exception as exc:
        return make_response(jsonify({'messages': exc.args})), 400  # type: ignore


class CreatingCatalogPresenter(CreatingCatalogResponseBoundary):
    response: Response

    def present(self, response_dto: CreatingCatalogResponse):
        self.response = make_response(jsonify(response_dto.__dict__))
