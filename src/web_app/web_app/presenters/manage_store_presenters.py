#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Response, make_response, jsonify
from store.application.usecases.manage.update_store_settings_uc import UpdatingStoreSettingsResponseBoundary, \
    UpdatingStoreSettingsResponse

from store.application.usecases.choose_store_plan_uc import ChoosenStorePlanResponseBoundary, ChoosenStorePlanResponse
from store.application.usecases.initialize.confirm_store_registration_uc import \
    ConfirmingStoreRegistrationResponseBoundary, ConfirmingStoreRegistrationResponse

from store.application.usecases.initialize.register_store_uc import RegisteringStoreResponseBoundary, \
    RegisteringStoreResponse
from store.application.usecases.manage.add_store_manager import AddingStoreManagerResponse, \
    AddingStoreManagerResponseBoundary
from store.application.usecases.manage.upload_image_uc import UploadingImageResponseBoundary, UploadingImageResponse


class RegisteringStorePresenter(RegisteringStoreResponseBoundary):
    response: Response

    def present(self, response_dto: RegisteringStoreResponse) -> None:
        self.response = make_response(jsonify(response_dto.__dict__))


class ConfirmingStoreRegistrationPresenter(ConfirmingStoreRegistrationResponseBoundary):
    response: Response

    def present(self, response_dto: ConfirmingStoreRegistrationResponse):
        self.response = make_response(jsonify(response_dto.__dict__))


class ChoosenStorePlanPresenter(ChoosenStorePlanResponseBoundary):
    response: Response

    def present(self, response_dto: ChoosenStorePlanResponse):
        self.response = make_response(jsonify(response_dto.__dict__))


class AddingStoreManagerPresenter(AddingStoreManagerResponseBoundary):
    response: Response

    def present(self, response_dto: AddingStoreManagerResponse):
        self.response = make_response(jsonify(response_dto.__dict__))


class UpdatingStoreSettingsPresenter(UpdatingStoreSettingsResponseBoundary):
    response: Response

    def present(self, response_dto: UpdatingStoreSettingsResponse):
        self.response = make_response(jsonify(response_dto.__dict__))


class UploadingImagePresenter(UploadingImageResponseBoundary):
    response: Response

    def present(self, response_dto: UploadingImageResponse):
        self.response = make_response(jsonify(response_dto.__dict__))
