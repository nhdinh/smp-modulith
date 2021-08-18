#!/usr/bin/env python
# -*- coding: utf-8 -*-
import flask_injector
import injector
from flask import Blueprint, Response, request, make_response, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from shop.application.queries.shop_queries import ListShopAddressesQuery, ListShopAddressesRequest, GetShopInfoQuery, \
  GetShopInfoRequest
from shop.application.usecases.catalog.add_shop_brand_uc import AddingShopBrandResponseBoundary, AddShopBrandUC, \
  AddingShopBrandRequest
from shop.application.usecases.catalog.add_shop_supplier_uc import AddingShopSupplierResponseBoundary, \
  AddShopSupplierUC, AddingShopSupplierRequest
from shop.application.usecases.initialize.confirm_shop_registration_uc import (
  ConfirmingShopRegistrationRequest,
  ConfirmingShopRegistrationResponseBoundary,
  ConfirmShopRegistrationUC,
)
from shop.application.usecases.initialize.register_shop_uc import (
  RegisteringShopRequest,
  RegisteringShopResponseBoundary,
  RegisterShopUC,
)
from shop.application.usecases.shop.add_shop_address_uc import AddingShopAddressResponseBoundary, AddShopAddressUC, \
  AddingShopAddressRequest
from shop.application.usecases.shop.add_shop_user_uc import AddShopUserUC, AddingShopUserRequest, \
  AddingShopUserResponseBoundary
from shop.application.usecases.shop.upload_image_uc import UploadImageUC, UploadingImageResponseBoundary, \
  UploadingImageRequest
from web_app.presenters import log_error
from web_app.presenters.shop_presenters import RegisteringShopPresenter, AddingShopAddressPresenter, \
  AddingShopSupplierPresenter, AddingShopBrandPresenter, AddingShopUserPresenter, UploadingImagePresenter, \
  ConfirmingShopRegistrationPresenter
from web_app.serialization.dto import get_dto

SHOP_BLUEPRINT_NAME = 'shop_blueprint'
shop_blueprint = Blueprint(SHOP_BLUEPRINT_NAME, __name__)


class ShopAPI(injector.Module):
  @injector.provider
  @flask_injector.request
  def register_shop_response_boundary(self) -> RegisteringShopResponseBoundary:
    return RegisteringShopPresenter()

  @injector.provider
  @flask_injector.request
  def confirm_shop_registration_response_boundary(self) -> ConfirmingShopRegistrationResponseBoundary:
    return ConfirmingShopRegistrationPresenter()

  @injector.provider
  @flask_injector.request
  def add_shop_manager_response_boundary(self) -> AddingShopUserResponseBoundary:
    return AddingShopUserPresenter()

  @injector.provider
  @flask_injector.request
  def add_shop_address_response_boundary(self) -> AddingShopAddressResponseBoundary:
    return AddingShopAddressPresenter()

  @injector.provider
  @flask_injector.request
  def add_shop_brand_response_boundary(self) -> AddingShopBrandResponseBoundary:
    return AddingShopBrandPresenter()

  @injector.provider
  @flask_injector.request
  def add_shop_supplier_response_boundary(self) -> AddingShopSupplierResponseBoundary:
    return AddingShopSupplierPresenter()

  @injector.provider
  @flask_injector.request
  def upload_image_response_boudary(self) -> UploadingImageResponseBoundary:
    return UploadingImagePresenter()


@shop_blueprint.route('/register', methods=['POST'])
@log_error()
def register_new_shop(register_shop_uc: RegisterShopUC, presenter: RegisteringShopResponseBoundary) -> Response:
  # try:
  dto = get_dto(request, RegisteringShopRequest, context={})
  register_shop_uc.execute(dto)
  return presenter.response, 201  # type: ignore


@shop_blueprint.route('/confirm', methods=['POST'])
@log_error()
def confirm_registration(confirm_registration_uc: ConfirmShopRegistrationUC,
                         presenter: ConfirmingShopRegistrationResponseBoundary) -> Response:
  dto = get_dto(request, ConfirmingShopRegistrationRequest, context={})
  confirm_registration_uc.execute(dto)
  return presenter.response, 201  # type: ignore


@shop_blueprint.route('/get_info', methods=['POST'])
@jwt_required()
@log_error()
def get_shop_info(get_shop_info_query: GetShopInfoQuery) -> Response:
  dto = get_dto(request, GetShopInfoRequest, context={'current_user_id': get_jwt_identity()})
  shop_info = get_shop_info_query.query(dto)

  return make_response(jsonify(shop_info)), 200  # type:ignore


@shop_blueprint.route('/list_users', methods=['GET', 'POST'])
@jwt_required()
@log_error()
def list_shop_managers():
  ...


@shop_blueprint.route('/add_user', methods=['POST'])
@jwt_required()
@log_error()
def add_shop_user(add_shop_user_uc: AddShopUserUC, presenter: AddingShopUserResponseBoundary) -> Response:
  dto = get_dto(request, AddingShopUserRequest, context={'current_user_id': get_jwt_identity()})
  add_shop_user_uc.execute(dto)

  return presenter.response, 201  # type: ignore


@shop_blueprint.route('/list_addresses', methods=['GET', 'POST'])
@jwt_required()
@log_error()
def list_shop_addresses(list_shop_addresses_query: ListShopAddressesQuery) -> Response:
  dto = get_dto(request, ListShopAddressesRequest, context={'current_user_id': get_jwt_identity()})
  addresses = list_shop_addresses_query.query(dto)

  return make_response(jsonify(addresses)), 200  # type:ignore


@shop_blueprint.route('/add_address', methods=['POST'])
@jwt_required()
@log_error()
def add_shop_address(add_shop_address_uc: AddShopAddressUC, presenter: AddingShopAddressResponseBoundary) -> Response:
  dto = get_dto(request, AddingShopAddressRequest, context={'current_user_id': get_jwt_identity()})
  add_shop_address_uc.execute(dto)

  return presenter.response, 201  # type: ignore


@shop_blueprint.route('/add_brand', methods=['POST'])
@jwt_required()
@log_error()
def add_shop_brand(add_shop_brand_uc: AddShopBrandUC, presenter: AddingShopBrandResponseBoundary) -> Response:
  dto = get_dto(request, AddingShopBrandRequest, context={'current_user_id': get_jwt_identity()})
  add_shop_brand_uc.execute(dto)

  return presenter.response, 201  # type:ignore


@shop_blueprint.route('/add_supplier', methods=['POST'])
@jwt_required()
@log_error()
def add_shop_supplier(add_shop_supplier_uc: AddShopSupplierUC,
                      presenter: AddingShopSupplierResponseBoundary) -> Response:
  dto = get_dto(request, AddingShopSupplierRequest, context={'current_user_id': get_jwt_identity()})
  add_shop_supplier_uc.execute(dto)

  return presenter.response, 201  # type:ignore


@shop_blueprint.route('/upload', methods=['POST'])
@jwt_required()
@log_error()
def upload_image(upload_image_uc: UploadImageUC, presenter: UploadingImageResponseBoundary) -> Response:
  dto = get_dto(request, UploadingImageRequest, context={'current_user_id': get_jwt_identity()})

  if 'file' not in request.files:
    raise Exception('No file input')

  uploaded_file = request.files['file']
  upload_image_uc.execute(uploaded_file, dto)

  return presenter.response, 201  # type:ignore

# TODO: Add image checker
# @shop_blueprint.route('/image', methods=['POST'])
# @validate_request_timestamp
# @jwt_required()
# @log_error()
# def get_image(image_checker: ImageCheckerUC) -> Response:
#     dto = get_dto(request, CheckingImageRequest, context={'current_user_id': get_jwt_identity()})
#     return_data = image_checker.check(dto)
#
#     return make_response(jsonify(return_data)), 200  # type:ignore
