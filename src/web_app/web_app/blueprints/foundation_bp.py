#!/usr/bin/env python
# -*- coding: utf-8 -*-
import flask_injector
import injector
from flask import Blueprint

from shop.application.usecases.shop.upload_image_uc import UploadingImageResponseBoundary

FOUNDATION_BLUEPRINT_NAME = 'foundation_blueprint'
foundation_blueprint = Blueprint(FOUNDATION_BLUEPRINT_NAME, __name__)


class FoundationAPI(injector.Module):
    @injector.provider
    @flask_injector.request
    def upload_image_response_boudary(self) -> UploadingImageResponseBoundary:
        return None

        # return UploadingImagePresenter()

# @foundation_blueprint.route('/upload_image', methods=['POST'])
# @jwt_required()
# @log_error()
# def upload_image(upload_image_uc: UploadImageUC, presenter: UploadingImageResponseBoundary):
#     dto = get_dto(request, UploadingImageRequest, context={'current_user_id': get_jwt_identity()})
#     upload_image_uc.execute(dto)
#
#     return presenter.response, 201  # type: ignore
