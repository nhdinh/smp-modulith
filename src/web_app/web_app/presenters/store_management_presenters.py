#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Response, jsonify, make_response

from shop.application.usecases.catalog.add_shop_brand_uc import AddingShopBrandResponseBoundary, AddingShopBrandResponse
from shop.application.usecases.catalog.add_shop_supplier_uc import AddingShopSupplierResponse, \
    AddingShopSupplierResponseBoundary
from shop.application.usecases.create_store_warehouse_uc import (
    CreatingStoreWarehouseResponse,
    CreatingStoreWarehouseResponseBoundary,
)
from shop.application.usecases.initialize.confirm_shop_registration_uc import (
    ConfirmingShopRegistrationResponse,
    ConfirmingShopRegistrationResponseBoundary,
)
from shop.application.usecases.select_store_plan_uc import SelectingShopPlanResponse, SelectingShopPlanResponseBoundary
from shop.application.usecases.shop.add_shop_address_uc import AddingShopAddressResponseBoundary, \
    AddingShopAddressResponse
from shop.application.usecases.shop.add_shop_user_uc import AddingShopUserResponseBoundary, \
    AddingShopUserResponse

from shop.application.usecases.shop.resend_store_registration_confirmation_uc import (
    ResendingRegistrationConfirmationResponse,
    ResendingRegistrationConfirmationResponseBoundary,
)
from shop.application.usecases.shop.update_store_settings_uc import (
    UpdatingStoreSettingsResponse,
    UpdatingStoreSettingsResponseBoundary,
)
from shop.application.usecases.shop.upload_image_uc import UploadingImageResponse, UploadingImageResponseBoundary


class ResendingRegistrationResponsePresenter(ResendingRegistrationConfirmationResponseBoundary):
    response: Response

    def present(self, response_dto: ResendingRegistrationConfirmationResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))


class ConfirmingShopRegistrationPresenter(ConfirmingShopRegistrationResponseBoundary):
    response: Response

    def present(self, response_dto: ConfirmingShopRegistrationResponse):
        self.response = make_response(jsonify(response_dto.__dict__))


class SelectingStorePlanPresenter(SelectingShopPlanResponseBoundary):
    response: Response

    def present(self, response_dto: SelectingShopPlanResponse):
        self.response = make_response(jsonify(response_dto.__dict__))


class AddingShopUserPresenter(AddingShopUserResponseBoundary):
    response: Response

    def present(self, response_dto: AddingShopUserResponse):
        self.response = make_response(jsonify(response_dto.__dict__))


class UpdatingStoreSettingsPresenter(UpdatingStoreSettingsResponseBoundary):
    response: Response

    def present(self, response_dto: UpdatingStoreSettingsResponse):
        self.response = make_response(jsonify(response_dto.__dict__))


class CreatingStoreWarehousePresenter(CreatingStoreWarehouseResponseBoundary):
    response: Response

    def present(self, response_dto: CreatingStoreWarehouseResponse):
        self.response = make_response(jsonify(response_dto.__dict__))


class UploadingImagePresenter(UploadingImageResponseBoundary):
    response: Response

    def present(self, response_dto: UploadingImageResponse):
        self.response = make_response(jsonify(response_dto.__dict__))


class AddingShopAddressPresenter(AddingShopAddressResponseBoundary):
    response: Response

    def present(self, response_dto: AddingShopAddressResponse):
        self.response = make_response(jsonify(response_dto.__dict__))


class AddingShopBrandPresenter(AddingShopBrandResponseBoundary):
    response: Response

    def present(self, response_dto: AddingShopBrandResponse):
        self.response = make_response(jsonify(response_dto.__dict__))


class AddingShopSupplierPresenter(AddingShopSupplierResponseBoundary):
    response: Response

    def present(self, response_dto: AddingShopSupplierResponse):
        self.response = make_response(jsonify(response_dto.__dict__))
