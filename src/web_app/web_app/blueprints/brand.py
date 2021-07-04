#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector
from flask import Blueprint, jsonify, make_response, Response, current_app

from product_catalog.application.queries.product_catalog import ListProductBrandsQuery

brand_blueprint = Blueprint('brand_blueprint', __name__)


class BrandAPI(injector.Module):
    pass


@brand_blueprint.route('/')
def fetch_all_brands(query: ListProductBrandsQuery) -> Response:
    try:
        brands = query.query()
        return make_response(jsonify(brands)), 200  # type:ignore
    except Exception as exc:
        if current_app.debug:
            raise exc

        return make_response(jsonify({'message': exc.args})), 400  # type:ignore
