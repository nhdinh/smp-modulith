#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, make_response, Response, abort, request
from flask_login import current_user

from product_catalog.application.create_catalog import CreatingCatalogOutputBoundary, CreatingCatalogResponse
from product_catalog.application.queries.product_catalog import GetAllCatalogsQuery, GetCatalogQuery
from web_app.serialization.dto import get_dto

catalog_blueprint = Blueprint('catalog_blueprint', __name__)


# class ProductCatalogAPI(injector.Module):
#     @injector.provider
#     @flask_injector.request
#     def return_something_boundary(self):
#         return None


@catalog_blueprint.route('/')
def list_all_catalog(query: GetAllCatalogsQuery) -> Response:
    return make_response(jsonify(query.query()))


@catalog_blueprint.route("/<string:catalog_reference>", methods=['GET'])
def get_catalow(catalog_reference: str, query: GetCatalogQuery):
    return make_response(jsonify(query.query(reference=catalog_reference)))


@catalog_blueprint.route('/', methods=['POST'])
def create_new_catalog(presenter: CreatingCatalogOutputBoundary) -> Response:
    if not current_user.is_authenticated:
        abort(403)

    dto = get_dto(request, CreateCatalogDto, context={})
    create_catalog_uc.execute(dto)
    return presenter.response


class CreatingCatalogPresenter(CreatingCatalogOutputBoundary):
    repsonse: Response

    def present(self, output_dto: CreatingCatalogResponse):
        message = 'Catalog created'
        self.response = make_response(jsonify({'message': message}))
