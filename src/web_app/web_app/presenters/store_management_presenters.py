#!/usr/bin/env python
# -*- coding: utf-8 -*-


class ResendingRegistrationResponsePresenter(ResendingRegistrationConfirmationResponseBoundary):
  response: Response

  def present(self, response_dto: ResendingRegistrationConfirmationResponse) -> None:
    self.response = make_response(jsonify(response_dto.__dict__))


class SelectingStorePlanPresenter(SelectingShopPlanResponseBoundary):
  response: Response

  def present(self, response_dto: SelectingShopPlanResponse):
    self.response = make_response(jsonify(response_dto.__dict__))


class UpdatingStoreSettingsPresenter(UpdatingStoreSettingsResponseBoundary):
  response: Response

  def present(self, response_dto: UpdatingStoreSettingsResponse):
    self.response = make_response(jsonify(response_dto.__dict__))


class CreatingStoreWarehousePresenter(CreatingStoreWarehouseResponseBoundary):
  response: Response

  def present(self, response_dto: CreatingStoreWarehouseResponse):
    self.response = make_response(jsonify(response_dto.__dict__))
