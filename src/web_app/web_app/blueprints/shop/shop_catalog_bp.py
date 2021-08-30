#!/usr/bin/env python
# -*- coding: utf-8 -*-

import flask_injector
import injector
from flask import Blueprint, Response, jsonify, make_response, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from shop.application.queries.catalog_queries import ListShopCatalogsQuery, ListShopProductsByCatalogQuery, \
    ListShopProductsByCatalogRequest, ListShopCatalogsRequest, ListActiveShopCatalogsQuery, ListActiveShopCatalogsRequest
from shop.application.usecases.catalog.add_shop_catalog_uc import (
    AddingShopCatalogRequest,
    AddingShopCatalogResponseBoundary,
    AddShopCatalogUC,
)
from shop.application.usecases.catalog.add_shop_collection_uc import AddShopCollectionUC, \
    AddingShopCollectionResponseBoundary, AddingShopCollectionRequest
from shop.application.usecases.catalog.remove_shop_catalog_uc import (
    RemoveShopCatalogUC,
    RemovingShopCatalogRequest,
    RemovingShopCatalogResponseBoundary,
)
from shop.application.usecases.catalog.set_shop_catalogs_status_uc import SetShopCatalogsStatusUC, \
    SettingShopCatalogsStatusResponseBoundary, SettingShopCatalogsStatusRequest
from shop.application.usecases.catalog.update_shop_catalog_uc import UpdatingShopCatalogResponseBoundary, \
    UpdateShopCatalogUC, UpdatingShopCatalogRequest
from web_app.helpers import validate_request_timestamp
from web_app.presenters import log_error
from web_app.presenters.shop_catalog_presenters import AddingShopCatalogPresenter, RemovingShopCatalogPresenter, \
    AddingShopCollectionPresenter, UpdatingShopCatalogPresenter, SettingShopCatalogsStatusPresenter
from web_app.serialization.dto import get_dto

SHOP_CATALOG_BLUEPRINT_NAME = 'shop_catalog_blueprint'
shop_catalog_blueprint = Blueprint(SHOP_CATALOG_BLUEPRINT_NAME, __name__)


class ShopCatalogAPI(injector.Module):
    @injector.provider
    @flask_injector.request
    def add_shop_catalog_response_boundary(self) -> AddingShopCatalogResponseBoundary:
        return AddingShopCatalogPresenter()

    @injector.provider
    @flask_injector.request
    def remove_shop_catalog_response_boundary(self) -> RemovingShopCatalogResponseBoundary:
        return RemovingShopCatalogPresenter()

    @injector.provider
    @flask_injector.request
    def add_shop_catalog_response_boundary(self) -> AddingShopCatalogResponseBoundary:
        return AddingShopCatalogPresenter()

    @injector.provider
    @flask_injector.request
    def add_shop_collection_response_boundary(self) -> AddingShopCollectionResponseBoundary:
        return AddingShopCollectionPresenter()

    @injector.provider
    @flask_injector.request
    def update_shop_catalog_boundary(self) -> UpdatingShopCatalogResponseBoundary:
        return UpdatingShopCatalogPresenter()

    @injector.provider
    @flask_injector.request
    def set_shop_catalogs_status_bounday(self) -> SettingShopCatalogsStatusResponseBoundary:
        return SettingShopCatalogsStatusPresenter()


@shop_catalog_blueprint.route('/list', methods=['GET', 'POST'])
@validate_request_timestamp
@jwt_required()
@log_error()
def list_shop_catalogs(list_shop_catalog_query: ListShopCatalogsQuery) -> Response:
    dto = get_dto(request, ListShopCatalogsRequest, context={'current_user_id': get_jwt_identity()})
    response = list_shop_catalog_query.query(dto)
    return make_response(jsonify(response)), 200  # type:ignore


@shop_catalog_blueprint.route('/list_all', methods=['GET', 'POST'])
@validate_request_timestamp
@jwt_required()
@log_error()
def list_active_shop_catalogs(list_active_shop_catalog_query: ListActiveShopCatalogsQuery) -> Response:
    dto = get_dto(request, ListActiveShopCatalogsRequest, context={'current_user_id': get_jwt_identity()})
    response = list_active_shop_catalog_query.query(dto)

    return make_response(jsonify(response)), 200  # type:ignore


@shop_catalog_blueprint.route('/list_products', methods=['GET', 'POST'])
@validate_request_timestamp
@jwt_required()
@log_error()
def list_shop_products_by_catalog(list_shop_products_by_catalog_query: ListShopProductsByCatalogQuery) -> Response:
    dto = get_dto(request, ListShopProductsByCatalogRequest, context={'current_user_id': get_jwt_identity()})
    response = list_shop_products_by_catalog_query.query(dto)
    return make_response(jsonify(response)), 200  # type:ignore


@shop_catalog_blueprint.route('/add', methods=['POST'])
@validate_request_timestamp
@jwt_required()
@log_error()
def add_shop_catalog(add_shop_catalog_uc: AddShopCatalogUC,
                     presenter: AddingShopCatalogResponseBoundary) -> Response:
    dto = get_dto(request, AddingShopCatalogRequest, context={'current_user_id': get_jwt_identity()})
    add_shop_catalog_uc.execute(dto)

    return presenter.response, 201  # type:ignore


@shop_catalog_blueprint.route('/delete', methods=['POST'])
@jwt_required()
@log_error()
def remove_store_catalog(remove_store_catalog_uc: RemoveShopCatalogUC,
                         presenter: RemovingShopCatalogResponseBoundary) -> Response:
    dto = get_dto(request, RemovingShopCatalogRequest, context={'current_user_id': get_jwt_identity()})
    remove_store_catalog_uc.execute(dto)

    return presenter.response, 200  # type:ignore


@shop_catalog_blueprint.route('/add_collection', methods=['POST'])
@jwt_required()
@log_error()
def add_shop_collection(add_shop_collection_uc: AddShopCollectionUC,
                        presenter: AddingShopCollectionResponseBoundary) -> Response:
    dto = get_dto(request, AddingShopCollectionRequest, context={'current_user_id': get_jwt_identity()})
    add_shop_collection_uc.execute(dto)

    return presenter.response, 201  # type:ignore


@shop_catalog_blueprint.route('/update', methods=['POST', 'PATCH'])
@validate_request_timestamp
@jwt_required()
@log_error()
def update_shop_catalog(update_shop_catalog_uc: UpdateShopCatalogUC,
                        presenter: UpdatingShopCatalogResponseBoundary) -> Response:
    dto = get_dto(request, UpdatingShopCatalogRequest, context={'current_user_id': get_jwt_identity()})
    update_shop_catalog_uc.execute(dto)

    return presenter.response, 201  # type:ignore


@shop_catalog_blueprint.route('/set_status', methods=['POST', 'PATCH'])
@validate_request_timestamp
@jwt_required()
@log_error()
def set_shop_catalog_status(set_shop_catalog_status_uc: SetShopCatalogsStatusUC,
                            presenter: SettingShopCatalogsStatusResponseBoundary) -> Response:
    dto = get_dto(request, SettingShopCatalogsStatusRequest, context={'current_user_id': get_jwt_identity()})
    set_shop_catalog_status_uc.execute(dto)

    return presenter.response, 201  # type:ignore
