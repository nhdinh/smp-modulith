#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Response, jsonify, make_response

from shop.application.usecases.catalog.add_shop_brand_uc import AddingShopBrandResponseBoundary, AddingShopBrandResponse
from shop.application.usecases.catalog.add_shop_supplier_uc import AddingShopSupplierResponseBoundary, \
    AddingShopSupplierResponse
from shop.application.usecases.initialize.confirm_shop_registration_uc import (
    ConfirmingShopRegistrationResponseBoundary,
    ConfirmingShopRegistrationResponse
)
from shop.application.usecases.initialize.register_shop_uc import (
    RegisteringShopResponse,
    RegisteringShopResponseBoundary,
)
from shop.application.usecases.shop.add_shop_address_uc import (
    AddingShopAddressResponseBoundary,
    AddingShopAddressResponse
)
from shop.application.usecases.shop.add_shop_user_uc import AddingShopUserResponseBoundary, AddingShopUserResponse
from shop.application.usecases.shop.upload_image_uc import UploadingImageResponseBoundary, UploadingImageResponse


class RegisteringShopPresenter(RegisteringShopResponseBoundary):
    response: Response

    def present(self, response_dto: RegisteringShopResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))


class ConfirmingShopRegistrationPresenter(ConfirmingShopRegistrationResponseBoundary):
    response: Response

    def present(self, response_dto: ConfirmingShopRegistrationResponse):
        self.response = make_response(jsonify(response_dto.__dict__))


class AddingShopAddressPresenter(AddingShopAddressResponseBoundary):
    response: Response

    def present(self, response_dto: AddingShopAddressResponse):
        self.response = make_response(jsonify(response_dto.__dict__))


class AddingShopSupplierPresenter(AddingShopSupplierResponseBoundary):
    response: Response

    def present(self, response_dto: AddingShopSupplierResponse):
        self.response = make_response(jsonify(response_dto.__dict__))


class AddingShopBrandPresenter(AddingShopBrandResponseBoundary):
    response: Response

    def present(self, response_dto: AddingShopBrandResponse):
        self.response = make_response(jsonify(response_dto.__dict__))


class AddingShopUserPresenter(AddingShopUserResponseBoundary):
    response: Response

    def present(self, response_dto: AddingShopUserResponse):
        self.response = make_response(jsonify(response_dto.__dict__))


class UploadingImagePresenter(UploadingImageResponseBoundary):
    response: Response

    def present(self, response_dto: UploadingImageResponse):
        self.response = make_response(jsonify(response_dto.__dict__))
