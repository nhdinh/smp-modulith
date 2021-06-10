#!/usr/bin/env python
# -*- coding: utf-8 -*-

import flask_injector
import injector
from flask import Blueprint, Response, make_response, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from foundation.business_rule import BusinessRuleValidationError
from store.application.queries.store_queries import FetchAllStoreCatalogsQuery
from store.application.usecases.create_store_catalog_uc import CreatingStoreCatalogResponseBoundary, \
    CreateStoreCatalogUC, CreatingStoreCatalogRequest
from store.application.usecases.update_store_catalog_uc import UpdatingStoreCatalogResponseBoundary, \
    UpdatingStoreCatalogRequest, UpdateStoreCatalogUC
from store.application.usecases.toggle_store_catalog_uc import ToggleStoreCatalogUC, TogglingStoreCatalogRequest
from store.application.usecases.update_store_collection_uc import UpdatingStoreCollectionResponseBoundary, \
    UpdateStoreCollectionUC, UpdatingStoreCollectionRequest
from store.application.usecases.initialize_store_with_plan_uc import InitializingStoreWithPlanResponseBoundary, \
    InitializeStoreWithPlanUC
from web_app.presenters.store_catalog_presenters import CreatingStoreCatalogPresenter, UpdatingStoreCatalogPresenter, \
    UpdatingStoreCollectionPresenter, InitializingStoreWithPlanResponsePresenter
from web_app.serialization.dto import get_dto, AuthorizedPaginationInputDto

store_catalog_blueprint = Blueprint('store_catalog_blueprint', __name__)


class StoreCatalogAPI(injector.Module):
    @injector.provider
    @flask_injector.request
    def initialize_store_with_plan(self) -> InitializingStoreWithPlanResponseBoundary:
        return InitializingStoreWithPlanResponsePresenter()

    @injector.provider
    @flask_injector.request
    def create_store_catalog_response_boundary(self) -> CreatingStoreCatalogResponseBoundary:
        return CreatingStoreCatalogPresenter()

    @injector.provider
    @flask_injector.request
    def update_store_catalog_response_boundnary(self) -> UpdatingStoreCatalogResponseBoundary:
        return UpdatingStoreCatalogPresenter()

    @injector.provider
    @flask_injector.request
    def update_store_collection_response_boundary(self) -> UpdatingStoreCollectionResponseBoundary:
        return UpdatingStoreCollectionPresenter()


"""
INIT STORE
"""


@store_catalog_blueprint.route('/init', methods=['POST'])
@jwt_required()
def init_store_from_plan(initialize_store_with_plan_uc: InitializeStoreWithPlanUC,
                         presenter: InitializingStoreWithPlanResponseBoundary) -> Response:
    """
    POST :5000/store-catalog/init
    Init store with pre-defined plan
    """
    raise NotImplementedError


"""
STORE-CATALOG(S)
"""


@store_catalog_blueprint.route('/', methods=['GET'])
@jwt_required()
def fetch_store_catalogs(query: FetchAllStoreCatalogsQuery) -> Response:
    """
    GET :5000/store-catalog/
    Fetch catalogs from store
    """
    try:
        current_user = get_jwt_identity()
        dto = get_dto(request, AuthorizedPaginationInputDto, context={'current_user': current_user})
        response = query.query(dto)
        return make_response(jsonify(response)), 200  # type:ignore
    except Exception as exc:
        return make_response(jsonify({'message': exc.args})), 400  # type:ignore


@store_catalog_blueprint.route('/', methods=['POST'])
@jwt_required()
def create_store_catalog(create_store_catalog_uc: CreateStoreCatalogUC,
                         presenter: CreatingStoreCatalogResponseBoundary) -> Response:
    """
    POST :5000/store-catalog/
    Create a new catalog
    """
    try:
        current_user = get_jwt_identity()
        dto = get_dto(request, CreatingStoreCatalogRequest, context={'current_user': current_user})
        create_store_catalog_uc.execute(dto)

        return presenter.response, 201  # type:ignore
    except BusinessRuleValidationError as exc:
        return make_response(jsonify({'message': exc.details})), 400  # type: ignore
    except Exception as exc:
        if current_app.debug:
            raise exc
        return make_response(jsonify({'message': exc.args})), 400  # type:ignore


@store_catalog_blueprint.route('/catalog:<string:catalog_reference>', methods=['GET'])
@jwt_required()
def fetch_store_catalog_collections(catalog_reference: str) -> Response:
    """
    GET :5000/store-catalog/catalog:catalog_reference
    Fetch collections from catalog

    :param catalog_reference:
    """
    raise NotImplementedError


@store_catalog_blueprint.route('/catalog:<string:catalog_reference>', methods=['PATCH'])
@jwt_required()
def update_store_catalog(catalog_reference: str, update_store_catalog_uc: UpdateStoreCatalogUC,
                         presenter: UpdatingStoreCatalogPresenter) -> Response:
    """
    PATCH :5000/store-catalog/catalog:catalog_reference
    Update information of a catalog

    :param presenter:
    :param update_store_catalog_uc:
    :param catalog_reference:
    """
    try:
        dto = get_dto(request, UpdatingStoreCatalogRequest, context={
            'current_user': get_jwt_identity(),
            'catalog_reference': catalog_reference
        })
        update_store_catalog_uc.execute(dto)
        return presenter.response, 201  # type: ignore
    except BusinessRuleValidationError as exc:
        return make_response(jsonify({'message': exc.details})), 400  # type: ignore
    except Exception as exc:
        if current_app.debug:
            raise exc
        return make_response(jsonify({'messages': exc.args})), 400  # type: ignore


@store_catalog_blueprint.route('/catalog:<string:catalog_reference>/toggle', methods=['PATCH'])
@jwt_required()
def toggle_store_catalog(catalog_reference: str, toogle_store_catalog_uc: ToggleStoreCatalogUC,
                         presenter: UpdatingStoreCatalogPresenter) -> Response:
    """
    PATCH :5000/store-catalog/catalog:catalog_reference/toggle
    Enable/Disable a catalog

    :param presenter:
    :param toogle_store_catalog_uc:
    :param catalog_reference:
    """
    try:
        dto = get_dto(request, TogglingStoreCatalogRequest, context={
            'current_user': get_jwt_identity(),
            'catalog_reference': catalog_reference
        })
        toogle_store_catalog_uc.execute(dto)
        return presenter.response, 201  # type: ignore
    except BusinessRuleValidationError as exc:
        return make_response(jsonify({'message': exc.details})), 400  # type: ignore
    except Exception as exc:
        if current_app.debug:
            raise exc
        return make_response(jsonify({'messages': exc.args})), 400  # type: ignore


@store_catalog_blueprint.route('/catalog:<string:catalog_reference>', methods=['DELETE'])
@jwt_required()
def remove_store_catalog(catalog_reference: str) -> Response:
    """
    DELETE :5000/store-catalog/catalog:catalog_reference
    Delete a catalog with or without its contents

    :param catalog_reference:
    """
    raise NotImplementedError


"""
STORE-COLLECTION(S)
"""


@store_catalog_blueprint.route(
    '/catalog:<string:catalog_reference>',
    methods=['POST']
)
@jwt_required()
def add_catalog_collection(catalog_reference: str) -> Response:
    """
    POST :5000/store-catalog/catalog:catalog_reference
    Create new collection in a catalog

    :param catalog_reference:
    """
    raise NotImplementedError


@store_catalog_blueprint.route(
    '/catalog:<string:catalog_reference>/collection:<string:collection_reference>',
    methods=['PATCH']
)
@jwt_required()
def update_catalog_collection(
        catalog_reference: str,
        collection_reference: str,
        update_store_collection_uc: UpdateStoreCollectionUC,
        presenter: UpdatingStoreCollectionResponseBoundary
) -> Response:
    """
    PATCH :5000/store-catalog/catalog:catalog_reference/collection:collection_reference
    Update a collection

    :param presenter:
    :param update_store_collection_uc:
    :param catalog_reference:
    :param collection_reference:
    """
    try:
        dto = get_dto(request, UpdatingStoreCollectionRequest, context={
            'catalog_reference': catalog_reference,
            'collection_reference': collection_reference,
        })
        update_store_collection_uc.execute(dto)
        return presenter.response, 200  # type: ignore
    except BusinessRuleValidationError as exc:
        return make_response(jsonify({'message': exc.details})), 400  # type: ignore
    except Exception as exc:
        if current_app.debug:
            raise exc
        return make_response(jsonify({'messages': exc.args})), 400  # type: ignore


@store_catalog_blueprint.route(
    '/catalog:<string:catalog_reference>/collection:<string:collection_reference>/toggle',
    methods=['PATCH']
)
@jwt_required()
def toggle_catalog_collection(catalog_reference: str, collection_reference: str) -> Response:
    """
    PATCH :5000/store-catalog/catalog:catalog_reference/collection:collection_reference/toggle
    Enable/Disable a collection

    :param catalog_reference:
    :param collection_reference:
    """
    raise NotImplementedError


@store_catalog_blueprint.route(
    '/catalog:<string:catalog_reference>/collection:<string:collection_reference>',
    methods=['DELETE']
)
@jwt_required()
def remove_catalog_collection(catalog_reference: str, collection_reference: str) -> Response:
    """
    DELETE :5000/store-catalog/catalog:catalog_reference/collection:collection_reference
    Delete a collection

    :param catalog_reference:
    :param collection_reference:
    """
    raise NotImplementedError


"""
STORE-CATALOG-COLLECTION-PRODUCT(s)
"""


@store_catalog_blueprint.route(
    '/catalog:<string:catalog_reference>/collection:<string:collection_reference>',
    methods=['GET']
)
@jwt_required()
def fetch_collection_products(catalog_reference: str, collection_reference: str) -> Response:
    """
    GET :5000/store-catalog/catalog:catalog_reference/collection:collection_reference
    Fetch products in catalog/ collection

    :param catalog_reference:
    :param collection_reference:
    """
    raise NotImplementedError


@store_catalog_blueprint.route(
    '/catalog:<string:catalog_reference>/collection:<string:collection_reference>',
    methods=['POST']
)
@jwt_required()
def add_collection_product(catalog_reference: str, collection_reference: str) -> Response:
    """
    POST :5000/store-catalog/catalog:catalog_reference/collection:collection_reference
    Create new product in catalog/ collection

    :param catalog_reference:
    :param collection_reference:
    """
    raise NotImplementedError


@store_catalog_blueprint.route('/product:<string:product_id>', methods=['PATCH'])
@jwt_required()
def update_product(product_id: str):
    """
    PATCH :5000/store-catalog/product:product_id
    Update a product

    :param product_id:
    """
    raise NotImplementedError


@store_catalog_blueprint.route('/product:<string:product_id>/toggle', methods=['PATCH'])
@jwt_required()
def toggle_product(product_id: str):
    """
    PATCH :5000/store-catalog/product:product_id/toggle
    Enable/ Disable a product

    :param product_id:
    """
    raise NotImplementedError


@store_catalog_blueprint.route('/product:<string:product_id>', methods=['DELETE'])
@jwt_required()
def remove_product(product_id: str):
    """
    DELETE :5000/store-catalog/product:product_id
    Delete a product

    :param product_id:
    """
    raise NotImplementedError
