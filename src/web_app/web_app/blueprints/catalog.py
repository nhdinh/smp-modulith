#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, make_response, Response

from product_catalog.application.queries.product_catalog import GetAllCatalogsQuery, GetCatalogQuery

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
def create_new_catalog() -> Response:
    return make_response(jsonify({'message': 'NotImplementedError'}))
