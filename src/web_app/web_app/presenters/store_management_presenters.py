#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Response, jsonify, make_response

from shop.application.usecases.create_store_warehouse_uc import (
    CreatingStoreWarehouseResponse,
    CreatingStoreWarehouseResponseBoundary,
)
from shop.application.usecases.initialize.confirm_shop_registration_uc import (
    ConfirmingShopRegistrationResponse,
    ConfirmingShopRegistrationResponseBoundary,
)
from shop.application.usecases.manage.add_store_manager import (
    AddingStoreManagerResponse,
    AddingStoreManagerResponseBoundary,
)
from shop.application.usecases.manage.create_store_address_uc import (
    CreatingShopAddressResponse,
    CreatingShopAddressResponseBoundary,
)
from shop.application.usecases.manage.resend_store_registration_confirmation_uc import (
    ResendingRegistrationConfirmationResponse,
    ResendingRegistrationConfirmationResponseBoundary,
)
from shop.application.usecases.manage.update_store_settings_uc import (
    UpdatingStoreSettingsResponse,
    UpdatingStoreSettingsResponseBoundary,
)
from shop.application.usecases.manage.upload_image_uc import UploadingImageResponse, UploadingImageResponseBoundary
from shop.application.usecases.select_store_plan_uc import SelectingShopPlanResponse, SelectingShopPlanResponseBoundary


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


class AddingStoreManagerPresenter(AddingStoreManagerResponseBoundary):
    response: Response

    def present(self, response_dto: AddingStoreManagerResponse):
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


class CreatingStoreAddressPresenter(CreatingShopAddressResponseBoundary):
    response: Response

    def present(self, response_dto: CreatingShopAddressResponse):
        self.response = make_response(jsonify(response_dto.__dict__))
