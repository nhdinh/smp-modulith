#!/usr/bin/env python
# -*- coding: utf-8 -*-
import flask_injector
import injector
from flask import Blueprint, jsonify, make_response, Response

catalog_blueprint = Blueprint('catalog_blueprint', __name__)


@catalog_blueprint.route('/')
def list_all_catalog() -> Response:
    return make_response(jsonify({'message': 'NotImplementedError'}))


@catalog_blueprint.route('/', methods=['POST'])
def create_new_catalog() -> Response:
    return make_response(jsonify({'message': 'NotImplementedError'}))
