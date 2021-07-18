#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Response, make_response, jsonify

from store.application.usecases.create_store_warehouse_uc import CreatingStoreWarehouseResponse, \
    CreatingStoreWarehouseResponseBoundary
from store.application.usecases.initialize.confirm_shop_registration_uc import \
    ConfirmingShopRegistrationResponseBoundary, ConfirmingShopRegistrationResponse
from store.application.usecases.manage.add_store_manager import AddingStoreManagerResponse, \
    AddingStoreManagerResponseBoundary
from store.application.usecases.manage.create_store_address_uc import CreatingStoreAddressResponse, \
    CreatingStoreAddressResponseBoundary
from store.application.usecases.manage.resend_store_registration_confirmation_uc import \
    ResendingRegistrationConfirmationResponse, ResendingRegistrationConfirmationResponseBoundary
from store.application.usecases.manage.update_store_settings_uc import UpdatingStoreSettingsResponseBoundary, \
    UpdatingStoreSettingsResponse
from store.application.usecases.manage.upload_image_uc import UploadingImageResponseBoundary, UploadingImageResponse
from store.application.usecases.select_store_plan_uc import SelectingStorePlanResponseBoundary, \
    SelectingStorePlanResponse


class ResendingRegistrationResponsePresenter(ResendingRegistrationConfirmationResponseBoundary):
    response: Response

    def present(self, response_dto: ResendingRegistrationConfirmationResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))


class ConfirmingShopRegistrationPresenter(ConfirmingShopRegistrationResponseBoundary):
    response: Response

    def present(self, response_dto: ConfirmingShopRegistrationResponse):
        self.response = make_response(jsonify(response_dto.__dict__))


class SelectingStorePlanPresenter(SelectingStorePlanResponseBoundary):
    response: Response

    def present(self, response_dto: SelectingStorePlanResponse):
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


class CreatingStoreAddressPresenter(CreatingStoreAddressResponseBoundary):
    response: Response

    def present(self, response_dto: CreatingStoreAddressResponse):
        self.response = make_response(jsonify(response_dto.__dict__))
