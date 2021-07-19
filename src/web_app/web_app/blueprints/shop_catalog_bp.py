#!/usr/bin/env python
# -*- coding: utf-8 -*-
import flask_injector
import injector
from flask import Blueprint, Response, request, make_response, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from store.application.queries.store_queries import ListShopCatalogsQuery
from store.application.usecases.catalog.create_store_catalog_uc import AddingShopCatalogResponseBoundary, \
    AddShopCatalogUC, AddingShopCatalogRequest
from store.application.usecases.catalog.remove_shop_catalog_uc import RemoveShopCatalogUC, \
    RemovingShopCatalogResponseBoundary, RemovingShopCatalogRequest

from web_app.presenters import log_error
from web_app.presenters.store_catalog_presenters import AddingShopCatalogPresenter, RemovingShopCatalogPresenter
from web_app.serialization.dto import get_dto, AuthorizedPaginationInputDto

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


@shop_catalog_blueprint.route('/list', methods=['GET', 'POST'])
@jwt_required()
@log_error()
def list_shop_catalogs(list_shop_catalog_query: ListShopCatalogsQuery) -> Response:
    dto = get_dto(request, AuthorizedPaginationInputDto, context={'partner_id': get_jwt_identity()})
    response = list_shop_catalog_query.query(dto)
    return make_response(jsonify(response)), 200  # type:ignore


@shop_catalog_blueprint.route('/add', methods=['POST'])
@jwt_required()
@log_error()
def add_shop_catalog(add_shop_catalog_uc: AddShopCatalogUC,
                     presenter: AddingShopCatalogResponseBoundary) -> Response:
    dto = get_dto(request, AddingShopCatalogRequest, context={'partner_id': get_jwt_identity()})
    add_shop_catalog_uc.execute(dto)

    return presenter.response, 201  # type:ignore


@shop_catalog_blueprint.route('/delete', methods=['POST'])
@jwt_required()
@log_error()
def remove_store_catalog(remove_store_catalog_uc: RemoveShopCatalogUC,
                         presenter: RemovingShopCatalogResponseBoundary) -> Response:
    dto = get_dto(request, RemovingShopCatalogRequest, context={'partner_id': get_jwt_identity()})
    remove_store_catalog_uc.execute(dto)

    return presenter.response, 200  # type:ignore
