#!/usr/bin/env python
# -*- coding: utf-8 -*-
import flask_injector
import injector
from flask import Blueprint, Response, request, current_app, make_response, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from foundation.business_rule import BusinessRuleValidationError
from foundation.logger import logger
from store.application.usecases.catalog.create_store_catalog_uc import AddingShopCatalogResponseBoundary, \
    AddShopCatalogUC, AddingShopCatalogRequest

from web_app.presenters.store_catalog_presenters import AddingShopCatalogPresenter
from web_app.serialization.dto import get_dto

SHOP_CATALOG_BLUEPRINT_NAME = 'shop_catalog_blueprint'
shop_catalog_blueprint = Blueprint(SHOP_CATALOG_BLUEPRINT_NAME, __name__)

class ShopCatalogAPI(injector.Module):
    @injector.provider
    @flask_injector.request
    def add_shop_catalog_response_boundary(self) -> AddingShopCatalogResponseBoundary:
        return AddingShopCatalogPresenter()


@shop_catalog_blueprint.route('/add', methods=['POST'])
@jwt_required()
def add_shop_catalog(add_shop_catalog_uc: AddShopCatalogUC,
                     presenter: AddingShopCatalogResponseBoundary) -> Response:
    """
    POST :5000/shop_catalog/add
    Create a new catalog
    """
    try:
        current_user_id = get_jwt_identity()
        dto = get_dto(request, AddingShopCatalogRequest, context={'partner_id': current_user_id})
        add_shop_catalog_uc.execute(dto)

        return presenter.response, 201  # type:ignore
    except BusinessRuleValidationError as exc:
        return make_response(jsonify({'message': exc.details})), 422  # type: ignore
    except Exception as exc:
        if current_app.debug:
            logger.exception(exc)
        return make_response(jsonify({'message': exc.args})), 400  # type:ignore
