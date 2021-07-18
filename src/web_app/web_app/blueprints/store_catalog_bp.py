#!/usr/bin/env python
# -*- coding: utf-8 -*-
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import flask_injector
import injector
from flask import Blueprint, Response, make_response, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from foundation.business_rule import BusinessRuleValidationError
from foundation.logger import logger
from store.application.queries.store_queries import ListShopCatalogsQuery, ListStoreCollectionsQuery, \
    ListProductsFromCollectionQuery, ListProductsQuery, ListStoreProductsQuery, \
    ListStoreSuppliersQuery
from store.application.usecases.catalog.create_store_catalog_uc import AddingShopCatalogResponseBoundary
from store.application.usecases.catalog.invalidate_store_catalog_cache_uc import InvalidateStoreCatalogCacheUC
from store.application.usecases.catalog.remove_shop_catalog_uc import RemovingShopCatalogResponseBoundary
from store.application.usecases.catalog.systemize_store_catalog_uc import SystemizeStoreCatalogUC, \
    SystemizingStoreCatalogRequest
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
from store.application.usecases.product.create_store_product_uc import CreateStoreProductUC, \
    AddingShopProductResponseBoundary, AddingShopProductRequest
from store.application.usecases.product.remove_store_product_attribute_uc import RemovingStoreProductAttributeRequest, \
    RemoveStoreProductAttributeUC, RemovingStoreProductAttributeResponseBoundary
from store.application.usecases.product.remove_store_product_uc import RemovingStoreProductResponseBoundary
from store.application.usecases.product.update_store_product_uc import UpdatingStoreProductRequest, \
    UpdateStoreProductUC, UpdatingStoreProductResponseBoundary
from store.application.usecases.store_uc_common import GenericStoreActionRequest, GenericStoreResponseBoundary
from store.domain.entities.value_objects import ShopCatalogId, StoreCollectionId
from web_app.presenters.store_catalog_presenters import AddingShopCatalogPresenter, UpdatingStoreCatalogPresenter, \
    UpdatingStoreCollectionPresenter, InitializingStoreWithPlanResponsePresenter, GenericStoreResponsePresenter, \
    CreatingStoreCollectionPresenter, RemovingShopCatalogPresenter, AddingShopProductPresenter, \
    UpdatingStoreProductPresenter, RemovingStoreProductAttributePresenter, RemovingStoreProductPresenter
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
    def create_store_catalog_response_boundary(self) -> AddingShopCatalogResponseBoundary:
        return AddingShopCatalogPresenter()

    @injector.provider
    @flask_injector.request
    def update_store_catalog_response_boundary(self) -> UpdatingStoreCatalogResponseBoundary:
        return UpdatingStoreCatalogPresenter()

    @injector.provider
    @flask_injector.request
    def remove_store_catalog_response_boundary(self) -> RemovingShopCatalogResponseBoundary:
        return RemovingShopCatalogPresenter()

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
    def create_store_product_response_boundary(self) -> AddingShopProductResponseBoundary:
        return AddingShopProductPresenter()

    @injector.provider
    @flask_injector.request
    def update_store_product_response_boundary(self) -> UpdatingStoreProductResponseBoundary:
        return UpdatingStoreProductPresenter()

    @injector.provider
    @flask_injector.request
    def remove_store_product_attribute_response_boundary(self) -> RemovingStoreProductAttributeResponseBoundary:
        return RemovingStoreProductAttributePresenter()

    @injector.provider
    @flask_injector.request
    def remove_store_product_response_boundary(self) -> RemovingStoreProductResponseBoundary:
        return RemovingStoreProductPresenter()

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
def fetch_store_catalogs(list_store_catalogs_query: ListShopCatalogsQuery) -> Response:
    """
    GET :5000/store-catalog/
    Fetch catalogs from store
    """
    try:
        current_user = get_jwt_identity()
        dto = get_dto(request, AuthorizedPaginationInputDto, context={'current_user': current_user})
        response = list_store_catalogs_query.query(dto)
        return make_response(jsonify(response)), 200  # type:ignore
    except Exception as exc:
        if current_app.debug:
            logger.exception(exc)
        return make_response(jsonify({'message': exc.args})), 400  # type:ignore


store_catalog_blueprint_endpoint_callers.append(fetch_store_catalogs)


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


@store_catalog_blueprint.route('/catalog/<string:catalog_id>', methods=['GET'])
@jwt_required()
def list_store_collections(
        catalog_id: str,
        list_store_collections_query: ListStoreCollectionsQuery
) -> Response:
    """
    GET :5000/store-catalog/catalog/<catalog_id>
    Fetch collection from catalog

    :param list_store_collections_query:
    :param catalog_id:
    """
    try:
        current_user = get_jwt_identity()
        dto = get_dto(request, AuthorizedPaginationInputDto, context={'current_user': current_user})
        response = list_store_collections_query.query(catalog_id=catalog_id, dto=dto)
        return make_response(jsonify(response)), 200  # type:ignore
    except Exception as exc:
        if current_app.debug:
            logger.exception(exc)
        return make_response(jsonify({'message': exc.args})), 400  # type:ignore


@store_catalog_blueprint.route('/catalog/<string:catalog_id>', methods=['PATCH'])
@jwt_required()
def update_store_catalog(catalog_id: ShopCatalogId, update_store_catalog_uc: UpdateStoreCatalogUC,
                         presenter: UpdatingStoreCatalogResponseBoundary) -> Response:
    """
    PATCH :5000/store-catalog/catalog/<catalog_id>
    Update information of a catalog

    :param presenter:
    :param update_store_catalog_uc:
    :param catalog_id:
    """
    try:
        dto = get_dto(request, UpdatingStoreCatalogRequest, context={
            'current_user': get_jwt_identity(),
            'catalog_id': catalog_id
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
def toggle_store_catalog(catalog_reference: ShopCatalogId, toogle_store_catalog_uc: ToggleStoreCatalogUC,
                         presenter: UpdatingStoreCatalogResponseBoundary) -> Response:
    """
    PATCH :5000/store-catalog/catalog/<catalog_id>/toggle
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
    PATCH :5000/store-catalog/catalog/<catalog_id>/system
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


# endregion

# region ## StoreCollection Operation Endpoints ##


@store_catalog_blueprint.route('/catalog/<string:catalog_reference>', methods=['POST'])
@jwt_required()
def create_store_collection(catalog_reference: str,
                            create_store_collection_uc: CreateStoreCollectionUC,
                            presenter: CreatingStoreCollectionResponseBoundary) -> Response:
    """
    POST :5000/store-catalog/catalog/<catalog_id>
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
    PATCH :5000/store-catalog/catalog/<catalog_id>/collection/<collection_reference>
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
    PATCH :5000/store-catalog/catalog/<catalog_id>/collection/<collection_reference>/toggle
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
    PATCH :5000/store-catalog/catalog/<catalog_id>/collection/<collection_reference>/default
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
    DELETE :5000/store-catalog/catalog/<catalog_id>/collection/<collection_reference>
    Delete a collection

    :param catalog_reference:
    :param collection_reference:
    """
    raise NotImplementedError


# endregion

# region ## StoreProduct Operation Endpoints ##

@store_catalog_blueprint.route('/products', methods=['GET'])
@jwt_required()
def fetch_store_products(fetch_store_products_query: ListStoreProductsQuery):
    try:
        dto = get_dto(request, AuthorizedPaginationInputDto, context={
            'current_user': get_jwt_identity()
        })
        response = fetch_store_products_query.query(dto=dto)

        return make_response(jsonify(response)), 200  # type:ignore
    except Exception as exc:
        if current_app.debug:
            logger.exception(exc)
        return make_response(jsonify({'message': exc.args})), 400  # type:ignore


@store_catalog_blueprint.route(
    '/catalog/<string:catalog_id>/collection/<string:collection_id>',
    methods=['GET']
)
@jwt_required()
def list_store_products_by_collection(
        collection_id: StoreCollectionId,
        catalog_id: ShopCatalogId,
        list_store_products_by_collection_query: ListProductsFromCollectionQuery
) -> Response:
    """
    GET :5000/store-catalog/catalog/<catalog_id>/collection/<collection_id>
    Fetch products in catalog/ collection

    :param list_store_products_by_collection_query:
    :param catalog_id:
    :param collection_id:
    """
    try:
        current_user = get_jwt_identity()
        dto = get_dto(request, AuthorizedPaginationInputDto, context={
            'current_user': current_user,
            'collection_id': collection_id,
            'catalog_id': catalog_id
        })

        response = list_store_products_by_collection_query.query(
            collection_id=collection_id,
            catalog_id=catalog_id,
            dto=dto
        )

        return make_response(jsonify(response)), 200  # type:ignore
    except Exception as exc:
        if current_app.debug:
            logger.exception(exc)
        return make_response(jsonify({'message': exc.args})), 400  # type:ignore


@store_catalog_blueprint.route(
    '/catalog/<string:catalog_id>',
    methods=['GET']
)
@jwt_required()
def list_store_products(
        catalog_id: str,
        list_store_products_query: ListProductsQuery
) -> Response:
    """
    GET :5000/store-catalog/catalog/<catalog_id>
    :param catalog_id:
    :param list_store_products_query:
    :return:
    """
    try:
        current_user = get_jwt_identity()
        response = list_store_products_query.query(owner_email=current_user,
                                                   catalog_id=catalog_id)

        return make_response(jsonify(response)), 200  # type:ignore
    except Exception as exc:
        if current_app.debug:
            logger.exception(exc)
        return make_response(jsonify({'message': exc.args})), 400  # type:ignore


def create_store_product_common(dto: AddingShopProductRequest,
                                create_store_product_uc: CreateStoreProductUC,
                                presenter: AddingShopProductResponseBoundary) -> Response:
    try:
        create_store_product_uc.execute(dto)
        return presenter.response, 201  # type: ignore
    except Exception as exc:
        raise exc


@store_catalog_blueprint.route('/products', methods=['POST'])
@jwt_required()
def create_store_product_without_collection(create_store_product_uc: CreateStoreProductUC,
                                            presenter: AddingShopProductResponseBoundary) -> Response:
    """
    POST :5000/store-catalog/product
    Create new product free style

    :param create_store_product_uc: the use case in charge for creating store product
    :param presenter: the output formatter
    :return:
    """
    try:
        dto = get_dto(request, AddingShopProductRequest, context={'current_user': get_jwt_identity()})
        return create_store_product_common(dto, create_store_product_uc, presenter)
    except BusinessRuleValidationError as exc:
        return make_response(jsonify({'message': exc.details})), 400  # type: ignore
    except Exception as exc:
        if current_app.debug:
            logger.exception(exc)
        return make_response(jsonify({'messages': exc.args})), 400  # type: ignore


@store_catalog_blueprint.route(
    '/catalog/<string:catalog_id>/collection/<string:collection_id>',
    methods=['POST']
)
@jwt_required()
def create_store_product_with_collection(catalog_id: str,
                                         collection_id: str,
                                         create_store_product_uc: CreateStoreProductUC,
                                         presenter: AddingShopProductResponseBoundary) -> Response:
    """
    POST :5000/store-catalog/catalog/<catalog_id>/collection/<collection_reference>
    Create new product in catalog/ collection

    :param presenter:
    :param create_store_product_uc:
    :param catalog_id:
    :param collection_id:
    """
    try:
        dto = get_dto(request, AddingShopProductRequest, context={
            'current_user': get_jwt_identity(),
            'catalog_id': catalog_id,
            'collection_id': collection_id
        })
        return create_store_product_common(dto, create_store_product_uc, presenter)
    except BusinessRuleValidationError as exc:
        return make_response(jsonify({'message': exc.details})), 400  # type: ignore
    except Exception as exc:
        if current_app.debug:
            logger.exception(exc)
        return make_response(jsonify({'messages': exc.args})), 400  # type: ignore


@store_catalog_blueprint.route('/product/<string:product_id>', methods=['PATCH'])
@jwt_required()
def update_store_product(product_id: str,
                         update_store_product_uc: UpdateStoreProductUC,
                         presenter: UpdatingStoreProductResponseBoundary) -> Response:
    """
    PATCH :5000/store-catalog/product:product_id
    Update a product

    :param product_id:
    :param update_store_product_uc:
    :param presenter:
    """
    try:
        dto = get_dto(request, UpdatingStoreProductRequest, context={
            'current_user': get_jwt_identity(),
            'product_id': product_id,
        })

        update_store_product_uc.execute(dto)
        return presenter.response, 200  # type: ignore
    except BusinessRuleValidationError as exc:
        return make_response(jsonify({'message': exc.details})), 400  # type: ignore
    except Exception as exc:
        if current_app.debug:
            logger.exception(exc)
        return make_response(jsonify({'messages': exc.args})), 400  # type: ignore


@store_catalog_blueprint.route('/product/<string:product_id>/<string:attr_type>', methods=['DELETE'])
@jwt_required()
def delete_store_product_attribute(product_id: str, attr_type: str,
                                   remove_store_product_attribute_uc: RemoveStoreProductAttributeUC,
                                   presenter: RemovingStoreProductAttributeResponseBoundary) -> Response:
    try:
        dto = get_dto(request, RemovingStoreProductAttributeRequest, context={
            'current_user': get_jwt_identity(),
            'product_id': product_id,
            'attribute_type': attr_type
        })

        remove_store_product_attribute_uc.execute(dto)
        return presenter.response, 200  # type: ignore
    except BusinessRuleValidationError as exc:
        return make_response(jsonify({'message': exc.details})), 400  # type: ignore
    except Exception as exc:
        if current_app.debug:
            logger.exception(exc)
        return make_response(jsonify({'messages': exc.args})), 400  # type: ignore


@store_catalog_blueprint.route('/products/<string:product_id>/toggle', methods=['PATCH'])
@jwt_required()
def toggle_store_product(product_id: str):
    """
    PATCH :5000/store-catalog/product:product_id/toggle
    Enable/ Disable a product

    :param product_id:
    """
    raise NotImplementedError


@store_catalog_blueprint.route('/products/<string:product_id>', methods=['DELETE'])
@jwt_required()
def remove_store_product(product_id: str):
    """
    DELETE :5000/store-catalog/product:product_id
    Delete a product

    :param product_id:
    """
    raise NotImplementedError


# endregion

# region ## MISC ##


@store_catalog_blueprint.route('/suppliers', methods=['GET'])
@jwt_required()
def list_store_suppliers(list_store_suppliers_query: ListStoreSuppliersQuery) -> Response:
    try:
        current_user = get_jwt_identity()
        dto = get_dto(request, AuthorizedPaginationInputDto, context={'current_user': current_user})
        response = list_store_suppliers_query.query(dto)
        return make_response(jsonify(response)), 200  # type:ignore
    except Exception as exc:
        if current_app.debug:
            logger.exception(exc)
        return make_response(jsonify({'message': exc.args})), 400  # type:ignore


# endregion


@store_catalog_blueprint.route('/testsendmail', methods=['GET'])
def test_send_mail():
    EMAIL_HOST = 'smtp_server'
    EMAIL_PORT = 2525
    EMAIL_USERNAME = None
    EMAIL_PASSWORD = None
    EMAIL_FROM = 'admin@smp.io'
    email = {
        'title': 'Some title',
        'text': 'Some text',
        'html': 'Some html'
    }

    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        try:
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            msg = MIMEMultipart("alternative")
            msg["Subject"] = email['title']
            msg["From"] = EMAIL_FROM
            msg["To"] = EMAIL_FROM
            msg.attach(MIMEText(email['text'], "plain"))
            msg.attach(MIMEText(email['html'], "html"))

            server.sendmail(EMAIL_FROM, EMAIL_FROM, msg.as_string())
        except Exception as exc:
            logger.exception(exc)

    return make_response({'status': 'OK'}), 201
