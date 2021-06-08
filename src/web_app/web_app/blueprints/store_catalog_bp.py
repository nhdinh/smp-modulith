#!/usr/bin/env python
# -*- coding: utf-8 -*-
import flask_injector
import injector
from flask import Blueprint, Response, make_response, jsonify
from flask_jwt_extended import jwt_required

store_catalog_blueprint = Blueprint('store_catalog_blueprint', __name__)


class AClass:
    pass


class StoreCatalogAPI(injector.Module):
    @injector.provider
    @flask_injector.request
    def show_something(self) -> AClass:
        return AClass()


@store_catalog_blueprint.route('/', methods=['GET'])
def somedef() -> Response:
    return make_response({'hello': 'storeProduct'})


@store_catalog_blueprint.route('/init', methods=['POST'])
@jwt_required()
def init_store_from_plan() -> Response:
    raise NotImplementedError


"""
STORE-CATALOG(S)
"""


@store_catalog_blueprint.route('/catalog:view', methods=['GET'])
@jwt_required()
def fetch_store_catalog() -> Response:
    raise NotImplementedError


@store_catalog_blueprint.route('/catalog:add', methods=['POST'])
@jwt_required()
def add_store_catalog() -> Response:
    raise NotImplementedError


@store_catalog_blueprint.route('/catalog:<string:catalog_reference>', methods=['PATCH'])
@jwt_required()
def modify_store_catalog(catalog_reference: str) -> Response:
    raise NotImplementedError


@store_catalog_blueprint.route('/catalog:<string:catalog_reference>:toggle', methods=['PATCH'])
@jwt_required()
def toggle_store_catalog(catalog_reference: str) -> Response:
    raise NotImplementedError


@store_catalog_blueprint.route('/catalog:<string:catalog_reference>', methods=['DELETE'])
@jwt_required()
def remove_store_catalog(catalog_reference: str) -> Response:
    raise NotImplementedError


"""
STORE-COLLECTION(S)
"""


@store_catalog_blueprint.route('/catalog:<string:catalog_reference>/collection:add', methods=['POST'])
@jwt_required()
def add_store_collection(catalog_reference: str) -> Response:
    """
    URL /store-catalog/catalog:some-catalog/collection:add

    :param catalog_reference:
    """
    raise NotImplementedError


@store_catalog_blueprint.route('/catalog:<string:catalog_reference>/collection:<string:collection_reference>',
                               methods=['PATCH'])
@jwt_required()
def modify_store_collection(catalog_reference: str, collection_reference: str) -> Response:
    raise NotImplementedError


@store_catalog_blueprint.route('/catalog:<string:catalog_reference>/collection:<string:collection_reference>',
                               methods=['DELETE'])
@jwt_required()
def remove_store_collection(catalog_reference: str, collection_reference: str) -> Response:
    raise NotImplementedError
