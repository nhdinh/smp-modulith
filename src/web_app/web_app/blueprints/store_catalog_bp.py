#!/usr/bin/env python
# -*- coding: utf-8 -*-

import flask_injector
import injector
from flask import Blueprint, Response, make_response, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from store.application.usecases.product.create_store_product_uc import CreateStoreProductUC, \
    CreatingStoreProductResponseBoundary, CreatingStoreProductRequest

from foundation.logger import logger
from store.application.usecases.catalog.systemize_store_catalog_uc import SystemizeStoreCatalogUC, \
    SystemizingStoreCatalogRequest

from foundation.business_rule import BusinessRuleValidationError
from store.application.queries.store_queries import FetchAllStoreCatalogsQuery, FetchAllStoreCollectionsQuery, \
    FetchStoreProductsFromCollectionQuery
from store.application.usecases.catalog.create_store_catalog_uc import CreatingStoreCatalogResponseBoundary, \
    CreateStoreCatalogUC, CreatingStoreCatalogRequest
from store.application.usecases.catalog.invalidate_store_catalog_cache_uc import InvalidateStoreCatalogCacheUC
from store.application.usecases.catalog.remove_store_catalog_uc import RemovingStoreCatalogRequest, \
    RemoveStoreCatalogUC, RemovingStoreCatalogResponseBoundary
from store.application.usecases.catalog.toggle_store_catalog_uc import ToggleStoreCatalogUC, TogglingStoreCatalogRequest
from store.application.usecases.catalog.update_store_catalog_uc import UpdatingStoreCatalogResponseBoundary, \
    UpdatingStoreCatalogRequest, UpdateStoreCatalogUC
from store.application.usecases.collection.create_store_collection_uc import CreateStoreCollectionUC, \
    CreatingStoreCollectionResponseBoundary, CreatingStoreCollectionRequest
from store.application.usecases.collection.make_store_collection_default_uc import MakingStoreCollectionDefaultRequest, \
    MakeStoreCollectionDefaultUC
from store.application.usecases.collection.toggle_store_collection_uc import TogglingStoreCollectionRequest, \
    ToggleStoreCollectionUC
from store.application.usecases.collection.update_store_collection_uc import UpdatingStoreCollectionResponseBoundary, \
    UpdateStoreCollectionUC, UpdatingStoreCollectionRequest
from store.application.usecases.initialize.initialize_store_with_plan_uc import \
    InitializingStoreWithPlanResponseBoundary, \
    InitializeStoreWithPlanUC
from store.application.usecases.store_uc_common import GenericStoreActionRequest, GenericStoreResponseBoundary
from web_app.presenters.store_catalog_presenters import CreatingStoreCatalogPresenter, UpdatingStoreCatalogPresenter, \
    UpdatingStoreCollectionPresenter, InitializingStoreWithPlanResponsePresenter, GenericStoreResponsePresenter, \
    CreatingStoreCollectionPresenter, RemovingStoreCatalogPresenter, CreatingStoreProductPresenter
from web_app.serialization.dto import get_dto, AuthorizedPaginationInputDto

STORE_CATALOG_BLUEPRINT_NAME = 'store_catalog_blueprint'
store_catalog_blueprint = Blueprint(STORE_CATALOG_BLUEPRINT_NAME, __name__)
store_catalog_blueprint_endpoint_callers = []


class StoreCatalogAPI(injector.Module):
    @injector.provider
    @flask_injector.request
    def initialize_store_with_plan(self) -> InitializingStoreWithPlanResponseBoundary:
        return InitializingStoreWithPlanResponsePresenter()

    @injector.provider
    @flask_injector.request
    def generic_store_response_boundary(self) -> GenericStoreResponseBoundary:
        return GenericStoreResponsePresenter()

    # region ## Store Catalog Response Boundary Registering ##

    @injector.provider
    @flask_injector.request
    def create_store_catalog_response_boundary(self) -> CreatingStoreCatalogResponseBoundary:
        return CreatingStoreCatalogPresenter()

    @injector.provider
    @flask_injector.request
    def update_store_catalog_response_boundary(self) -> UpdatingStoreCatalogResponseBoundary:
        return UpdatingStoreCatalogPresenter()

    @injector.provider
    @flask_injector.request
    def remove_store_catalog_response_boundary(self) -> RemovingStoreCatalogResponseBoundary:
        return RemovingStoreCatalogPresenter()

    # endregion

    # region ## Store Collection Response Boundary Registering ##

    @injector.provider
    @flask_injector.request
    def create_store_collection_response_boundary(self) -> CreatingStoreCollectionResponseBoundary:
        return CreatingStoreCollectionPresenter()

    @injector.provider
    @flask_injector.request
    def update_store_collection_response_boundary(self) -> UpdatingStoreCollectionResponseBoundary:
        return UpdatingStoreCollectionPresenter()

    # endregion

    # region ## Store Product Response Boundary Registering ##

    @injector.provider
    @flask_injector.request
    def create_store_product_response_boundary(self) -> CreatingStoreProductResponseBoundary:
        return CreatingStoreProductPresenter()

    # endregion


# region ## Init Store Endpoints ##


@store_catalog_blueprint.route('/init', methods=['POST'])
@jwt_required()
def init_store_from_plan(initialize_store_with_plan_uc: InitializeStoreWithPlanUC,
                         presenter: InitializingStoreWithPlanResponseBoundary) -> Response:
    """
    POST :5000/store-catalog/init
    Init store with pre-defined plan
    """
    raise NotImplementedError


store_catalog_blueprint_endpoint_callers.append(init_store_from_plan)


# endregion

# region ## StoreCatalog Operation Endpoints ##


@store_catalog_blueprint.route('/', methods=['GET'])
@jwt_required()
def fetch_store_catalogs(fetch_all_store_catalogs_query: FetchAllStoreCatalogsQuery) -> Response:
    """
    GET :5000/store-catalog/
    Fetch catalogs from store
    """
    try:
        current_user = get_jwt_identity()
        dto = get_dto(request, AuthorizedPaginationInputDto, context={'current_user': current_user})
        response = fetch_all_store_catalogs_query.query(dto)
        return make_response(jsonify(response)), 200  # type:ignore
    except Exception as exc:
        if current_app.debug:
            logger.exception(exc)
        return make_response(jsonify({'message': exc.args})), 400  # type:ignore


store_catalog_blueprint_endpoint_callers.append(fetch_store_catalogs)


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
            logger.exception(exc)
        return make_response(jsonify({'message': exc.args})), 400  # type:ignore


@store_catalog_blueprint.route('/cache-invalidate', methods=['POST'])
@jwt_required()
def rebuild_store_catalog_cache(invalidate_store_catalog_cache_uc: InvalidateStoreCatalogCacheUC,
                                presenter: GenericStoreResponseBoundary) -> Response:
    """
    POST :5000/store-catalog/cache-invalidate
    Invalidate the catalog cache of a store

    :param invalidate_store_catalog_cache_uc:
    :param presenter:
    """
    try:
        current_user = get_jwt_identity()
        dto = get_dto(request, GenericStoreActionRequest, context={'current_user': current_user})
        invalidate_store_catalog_cache_uc.execute(dto)

        return presenter.response, 201  # type:ignore
    except BusinessRuleValidationError as exc:
        return make_response(jsonify({'message': exc.details})), 400  # type: ignore
    except Exception as exc:
        if current_app.debug:
            logger.exception(exc)
        return make_response(jsonify({'message': exc.args})), 400  # type:ignore


@store_catalog_blueprint.route('/catalog/<string:catalog_reference>', methods=['GET'])
@jwt_required()
def fetch_store_collections(
        catalog_reference: str,
        fetch_all_store_collections_query: FetchAllStoreCollectionsQuery
) -> Response:
    """
    GET :5000/store-catalog/catalog/<catalog_reference>
    Fetch collection from catalog

    :param fetch_all_store_collections_query:
    :param catalog_reference:
    """
    try:
        current_user = get_jwt_identity()
        dto = get_dto(request, AuthorizedPaginationInputDto, context={'current_user': current_user})
        response = fetch_all_store_collections_query.query(catalog_reference=catalog_reference, dto=dto)
        return make_response(jsonify(response)), 200  # type:ignore
    except Exception as exc:
        if current_app.debug:
            logger.exception(exc)
        return make_response(jsonify({'message': exc.args})), 400  # type:ignore


@store_catalog_blueprint.route('/catalog/<string:catalog_reference>', methods=['PATCH'])
@jwt_required()
def update_store_catalog(catalog_reference: str, update_store_catalog_uc: UpdateStoreCatalogUC,
                         presenter: UpdatingStoreCatalogResponseBoundary) -> Response:
    """
    PATCH :5000/store-catalog/catalog/<catalog_reference>
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
            logger.exception(exc)
        return make_response(jsonify({'messages': exc.args})), 400  # type: ignore


@store_catalog_blueprint.route('/catalog/<string:catalog_reference>/toggle', methods=['PATCH'])
@jwt_required()
def toggle_store_catalog(catalog_reference: str, toogle_store_catalog_uc: ToggleStoreCatalogUC,
                         presenter: UpdatingStoreCatalogResponseBoundary) -> Response:
    """
    PATCH :5000/store-catalog/catalog/<catalog_reference>/toggle
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
            logger.exception(exc)
        return make_response(jsonify({'messages': exc.args})), 400  # type: ignore


@store_catalog_blueprint.route('/catalog/<string:catalog_reference>/system', methods=['PATCH'])
@jwt_required()
def systemize_store_catalog(catalog_reference: str, systemize_store_catalog_uc: SystemizeStoreCatalogUC,
                            presenter: UpdatingStoreCatalogResponseBoundary) -> Response:
    """
    PATCH :5000/store-catalog/catalog/<catalog_reference>/system
    Make a catalog system

    :param presenter:
    :param systemize_store_catalog_uc:
    :param catalog_reference:
    """
    try:
        dto = get_dto(request, SystemizingStoreCatalogRequest, context={
            'current_user': get_jwt_identity(),
            'catalog_reference': catalog_reference
        })
        systemize_store_catalog_uc.execute(dto)
        return presenter.response, 201  # type: ignore
    except BusinessRuleValidationError as exc:
        return make_response(jsonify({'message': exc.details})), 400  # type: ignore
    except Exception as exc:
        if current_app.debug:
            logger.exception(exc)
        return make_response(jsonify({'messages': exc.args})), 400  # type: ignore


@store_catalog_blueprint.route('/catalog/<string:catalog_reference>', methods=['DELETE'])
@jwt_required()
def remove_store_catalog(catalog_reference: str,
                         remove_store_catalog_uc: RemoveStoreCatalogUC,
                         presenter: RemovingStoreCatalogResponseBoundary) -> Response:
    """
    DELETE :5000/store-catalog/catalog/<catalog_reference>
    Delete a catalog with or without its contents

    :param presenter:
    :param remove_store_catalog_uc:
    :param catalog_reference:
    """
    try:
        dto = get_dto(request, RemovingStoreCatalogRequest, context={
            'catalog_reference': catalog_reference,
            'current_user': get_jwt_identity()
        })
        remove_store_catalog_uc.execute(dto)

        return presenter.response, 200  # type: ignore
    except BusinessRuleValidationError as exc:
        return make_response(jsonify({'message': exc.details})), 400  # type: ignore
    except Exception as exc:
        if current_app.debug:
            logger.exception(exc)
        return make_response(jsonify({'messages': exc.args})), 400  # type: ignore


# endregion

# region ## StoreCollection Operation Endpoints ##


@store_catalog_blueprint.route('/catalog/<string:catalog_reference>', methods=['POST'])
@jwt_required()
def create_store_collection(catalog_reference: str,
                            create_store_collection_uc: CreateStoreCollectionUC,
                            presenter: CreatingStoreCollectionResponseBoundary) -> Response:
    """
    POST :5000/store-catalog/catalog/<catalog_reference>
    Create new collection in a catalog

    :param create_store_collection_uc:
    :param presenter:
    :param catalog_reference:
    """
    try:
        dto = get_dto(request, CreatingStoreCollectionRequest, context={
            'current_user': get_jwt_identity(),
            'catalog_reference': catalog_reference
        })
        create_store_collection_uc.execute(dto)
        return presenter.response, 201  # type: ignore
    except BusinessRuleValidationError as exc:
        return make_response(jsonify({'message': exc.details})), 400  # type: ignore
    except Exception as exc:
        if current_app.debug:
            logger.exception(exc)
        return make_response(jsonify({'messages': exc.args})), 400  # type: ignore


@store_catalog_blueprint.route(
    '/catalog/<string:catalog_reference>/collection/<string:collection_reference>',
    methods=['PATCH']
)
@jwt_required()
def update_store_collection(
        catalog_reference: str,
        collection_reference: str,
        update_store_collection_uc: UpdateStoreCollectionUC,
        presenter: UpdatingStoreCollectionResponseBoundary
) -> Response:
    """
    PATCH :5000/store-catalog/catalog/<catalog_reference>/collection/<collection_reference>
    Update a collection

    :param presenter:
    :param update_store_collection_uc:
    :param catalog_reference:
    :param collection_reference:
    """
    try:
        dto = get_dto(request, UpdatingStoreCollectionRequest, context={
            'current_user': get_jwt_identity(),
            'catalog_reference': catalog_reference,
            'collection_reference': collection_reference,
        })
        update_store_collection_uc.execute(dto)
        return presenter.response, 200  # type: ignore
    except BusinessRuleValidationError as exc:
        return make_response(jsonify({'message': exc.details})), 400  # type: ignore
    except Exception as exc:
        if current_app.debug:
            logger.exception(exc)
        return make_response(jsonify({'messages': exc.args})), 400  # type: ignore


@store_catalog_blueprint.route(
    '/catalog/<string:catalog_reference>/collection/<string:collection_reference>/toggle',
    methods=['PATCH']
)
@jwt_required()
def toggle_store_collection(catalog_reference: str, collection_reference: str,
                            toggle_store_collection_uc: ToggleStoreCollectionUC,
                            presenter: UpdatingStoreCollectionResponseBoundary) -> Response:
    """
    PATCH :5000/store-catalog/catalog/<catalog_reference>/collection/<collection_reference>/toggle
    Enable/Disable a collection

    :param presenter:
    :param toggle_store_collection_uc:
    :param catalog_reference:
    :param collection_reference:
    """

    try:
        dto = get_dto(request, TogglingStoreCollectionRequest, context={
            'current_user': get_jwt_identity(),
            'catalog_reference': catalog_reference,
            'collection_reference': collection_reference
        })
        toggle_store_collection_uc.execute(dto)
        return presenter.response, 201  # type: ignore
    except BusinessRuleValidationError as exc:
        return make_response(jsonify({'message': exc.details})), 400  # type: ignore
    except Exception as exc:
        if current_app.debug:
            logger.exception(exc)
        return make_response(jsonify({'messages': exc.args})), 400  # type: ignore


@store_catalog_blueprint.route(
    '/catalog/<string:catalog_reference>/collection/<string:collection_reference>/default',
    methods=['PATCH']
)
@jwt_required()
def make_store_collection_default(catalog_reference: str, collection_reference: str,
                                  make_store_collection_default_uc: MakeStoreCollectionDefaultUC,
                                  presenter: UpdatingStoreCollectionResponseBoundary) -> Response:
    """
    PATCH :5000/store-catalog/catalog/<catalog_reference>/collection/<collection_reference>/default
    Make this collection to be default collection

    :param presenter:
    :param make_store_collection_default_uc:
    :param catalog_reference:
    :param collection_reference:
    """

    try:
        dto = get_dto(request, MakingStoreCollectionDefaultRequest, context={
            'current_user': get_jwt_identity(),
            'catalog_reference': catalog_reference,
            'collection_reference': collection_reference
        })
        make_store_collection_default_uc.execute(dto)
        return presenter.response, 201  # type: ignore
    except BusinessRuleValidationError as exc:
        return make_response(jsonify({'message': exc.details})), 400  # type: ignore
    except Exception as exc:
        if current_app.debug:
            logger.exception(exc)
        return make_response(jsonify({'messages': exc.args})), 400  # type: ignore


@store_catalog_blueprint.route(
    '/catalog/<string:catalog_reference>/collection/<string:collection_reference>',
    methods=['DELETE']
)
@jwt_required()
def remove_store_collection(catalog_reference: str, collection_reference: str) -> Response:
    """
    DELETE :5000/store-catalog/catalog/<catalog_reference>/collection/<collection_reference>
    Delete a collection

    :param catalog_reference:
    :param collection_reference:
    """
    raise NotImplementedError


# endregion

# region ## StoreProduct Operation Endpoints ##


@store_catalog_blueprint.route(
    '/catalog/<string:catalog_reference>/collection/<string:collection_reference>',
    methods=['GET']
)
@jwt_required()
def fetch_store_products_from_collection(
        collection_reference: str,
        catalog_reference: str,
        fetch_store_products_from_collection_query: FetchStoreProductsFromCollectionQuery
) -> Response:
    """
    GET :5000/store-catalog/catalog/<catalog_reference>/collection/<collection_reference>
    Fetch products in catalog/ collection

    :param fetch_store_products_from_collection_query:
    :param catalog_reference:
    :param collection_reference:
    """
    try:
        current_user = get_jwt_identity()
        dto = get_dto(request, AuthorizedPaginationInputDto, context={
            'current_user': current_user,
            'collection_reference': collection_reference,
            'catalog_reference': catalog_reference
        })
        response = fetch_store_products_from_collection_query.query(
            collection_reference=collection_reference,
            catalog_reference=catalog_reference,
            dto=dto
        )
        return make_response(jsonify(response)), 200  # type:ignore
    except Exception as exc:
        if current_app.debug:
            logger.exception(exc)
        return make_response(jsonify({'message': exc.args})), 400  # type:ignore


def create_store_product_common(dto: CreatingStoreProductRequest,
                                create_store_product_uc: CreateStoreProductUC,
                                presenter: CreatingStoreProductResponseBoundary) -> Response:
    try:
        create_store_product_uc.execute(dto)
        return presenter.response, 201  # type: ignore
    except Exception as exc:
        raise exc


@store_catalog_blueprint.route('/products', methods=['POST'])
@jwt_required()
def create_store_product_without_collection(create_store_product_uc: CreateStoreProductUC,
                                            presenter: CreatingStoreProductResponseBoundary) -> Response:
    """
    POST :5000/store-catalog/product
    Create new product free style

    :param create_store_product_uc: the usecase in charge for creating store product
    :param presenter: the output formatter
    :return:
    """
    try:
        dto = get_dto(request, CreatingStoreProductRequest, context={'current_user': get_jwt_identity()})
        return create_store_product_common(dto, create_store_product_uc, presenter)
    except BusinessRuleValidationError as exc:
        return make_response(jsonify({'message': exc.details})), 400  # type: ignore
    except Exception as exc:
        if current_app.debug:
            logger.exception(exc)
        return make_response(jsonify({'messages': exc.args})), 400  # type: ignore


@store_catalog_blueprint.route(
    '/catalog/<string:catalog_reference>/collection/<string:collection_reference>',
    methods=['POST']
)
@jwt_required()
def create_store_product_with_collection(catalog_reference: str, collection_reference: str,
                                         create_store_product_uc: CreateStoreProductUC,
                                         presenter: CreatingStoreProductResponseBoundary) -> Response:
    """
    POST :5000/store-catalog/catalog/<catalog_reference>/collection/<collection_reference>
    Create new product in catalog/ collection

    :param presenter:
    :param create_store_product_uc:
    :param catalog_reference:
    :param collection_reference:
    """
    try:
        dto = get_dto(request, CreatingStoreProductRequest, context={
            'current_user': get_jwt_identity(),
            'catalog_reference': catalog_reference,
            'collection_reference': collection_reference
        })
        return create_store_product_common(dto, create_store_product_uc, presenter)
    except BusinessRuleValidationError as exc:
        return make_response(jsonify({'message': exc.details})), 400  # type: ignore
    except Exception as exc:
        if current_app.debug:
            logger.exception(exc)
        return make_response(jsonify({'messages': exc.args})), 400  # type: ignore


@store_catalog_blueprint.route('/product:<string:product_id>', methods=['PATCH'])
@jwt_required()
def update_store_product(product_id: str):
    """
    PATCH :5000/store-catalog/product:product_id
    Update a product

    :param product_id:
    """
    raise NotImplementedError


@store_catalog_blueprint.route('/product:<string:product_id>/toggle', methods=['PATCH'])
@jwt_required()
def toggle_store_product(product_id: str):
    """
    PATCH :5000/store-catalog/product:product_id/toggle
    Enable/ Disable a product

    :param product_id:
    """
    raise NotImplementedError


@store_catalog_blueprint.route('/product:<string:product_id>', methods=['DELETE'])
@jwt_required()
def remove_store_product(product_id: str):
    """
    DELETE :5000/store-catalog/product:product_id
    Delete a product

    :param product_id:
    """
    raise NotImplementedError

# endregion
