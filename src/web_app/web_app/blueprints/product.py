#!/usr/bin/env python
# -*- coding: utf-8 -*-

import flask_injector
import injector
from flask import Response, Blueprint, jsonify, make_response, request, current_app
from flask_jwt_extended import jwt_required

from foundation.business_rule import BusinessRuleValidationError
from product_catalog.application.queries.product_catalog import GetAllProductsQuery
from product_catalog.application.usecases.create_product import CreatingProductResponse, CreatingProductRequest, \
    CreateProductUC, CreatingProductResponseBoundary
from product_catalog.application.usecases.modify_product import ModifyingProductResponseBoundary, ModifyProductUC, \
    ModifyingProductResponse
from web_app.serialization.dto import get_dto

product_blueprint = Blueprint('product_blueprint', __name__)


class ProductAPI(injector.Module):
    @injector.provider
    @flask_injector.request
    def create_product_response_boundary(self) -> CreatingProductResponseBoundary:
        return CreatingProductPresenter()

    @injector.provider
    @flask_injector.request
    def modify_product_response_boundary(self) -> ModifyingProductResponseBoundary:
        return ModifyingProductPresenter()


@product_blueprint.route('/', methods=['GET'])
@jwt_required()
def list_all_products(query: GetAllProductsQuery) -> Response:
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)

        pagination = query.query(page=page, page_size=page_size)
        return make_response(jsonify(pagination)), 200  # type: ignore
    except Exception as exc:
        return make_response(jsonify({'message': exc.args})), 400  # type:ignore


@product_blueprint.route('/<string:catalog_query>', methods=['POST'])
@jwt_required()
def create_new_product_with_catalog(catalog_query: str, create_product_uc: CreateProductUC,
                                    presenter: CreatingProductResponseBoundary) -> Response:
    try:
        dto = get_dto(request, CreatingProductRequest, context={'catalog_query': catalog_query})
        create_product_uc.execute(dto)
        return presenter.response, 201  # type:ignore
    except BusinessRuleValidationError as exc:
        return make_response(jsonify({'message': exc.details})), 400  # type: ignore
    except Exception as exc:
        return make_response(jsonify({'messages': exc.args})), 400  # type: ignore


@product_blueprint.route('/', methods=['POST'])
# @jwt_required()
def create_new_product(create_product_uc: CreateProductUC, presenter: CreatingProductResponseBoundary) -> Response:
    try:
        dto = get_dto(request, CreatingProductRequest, context={})
        create_product_uc.execute(dto)
        return presenter.response, 201  # type:ignore
    except BusinessRuleValidationError as exc:
        return make_response(jsonify({'message': exc.details})), 400  # type: ignore
    except Exception as exc:
        if current_app.debug:
            raise exc
        return make_response(jsonify({'messages': exc.args})), 400  # type: ignore


@product_blueprint.route('/<string:product_query>', methods=['PATCH'])
def modify_product(product_query: str, modify_product_uc: ModifyProductUC,
                   presenter: ModifyingProductResponseBoundary) -> Response:
    try:

        return presenter.response, 200  # type:ignore
    except BusinessRuleValidationError as exc:
        return make_response(jsonify({'message': exc.details})), 400  # type: ignore
    except Exception as exc:
        return make_response(jsonify({'messages': exc.args})), 400  # type: ignore


class CreatingProductPresenter(CreatingProductResponseBoundary):
    response: Response

    def present(self, response_dto: CreatingProductResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))


class ModifyingProductPresenter(ModifyingProductResponseBoundary):
    response: Response

    def present(self, response_dto: ModifyingProductResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))
