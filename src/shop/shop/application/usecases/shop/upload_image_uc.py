#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from minio import Minio
from werkzeug.datastructures import FileStorage

from foundation.fs import FileSystem
from shop.application.services.shop_unit_of_work import ShopUnitOfWork
from shop.application.usecases.shop_uc_common import get_shop_or_raise
from shop.domain.entities.value_objects import ExceptionMessages
from web_app.serialization.dto import BaseAuthorizedShopUserRequest

ALLOWED_MIME_TYPES = {'image/jpg', 'image/jpeg', 'image/png'}


@dataclass
class UploadingImageRequest(BaseAuthorizedShopUserRequest):
  # file: fields.Raw(type='file')
  upload_for: Optional[str] = ''
  identity: Optional[str] = ''


@dataclass
class UploadingImageResponse:
  status: bool
  location: str
  bucket_name: str
  object_name: str


class UploadingImageResponseBoundary(abc.ABC):
  @abc.abstractmethod
  def present(self, response_dto: UploadingImageResponse):
    raise NotImplementedError


class UploadImageUC:
  def __init__(self, ob: UploadingImageResponseBoundary, uow: ShopUnitOfWork, minio_client: Minio, fs: FileSystem):
    self._ob = ob
    self._uow = uow
    self._minio = minio_client
    self._fs = fs

  def execute(self, uploaded_file: FileStorage, dto: UploadingImageRequest):
    with self._uow as uow:  # type:ShopUnitOfWork
      try:
        shop = get_shop_or_raise(shop_id=dto.shop_id, user_id=dto.current_user_id, uow=uow)

        # validate allowed file extension
        if uploaded_file.content_type not in ALLOWED_MIME_TYPES:
          raise Exception(ExceptionMessages.UNSUPPORTED_FILE_TYPE)

        # generate new file name
        upload_for = dto.upload_for if dto.upload_for else 'unassigned'
        identity = str(dto.identity) if dto.identity else str(uuid.uuid4())
        file_ext = Path(uploaded_file.filename).suffix
        new_file_name = f"{upload_for}_{identity}{file_ext}"

        bucket_name = str(shop.shop_id.lower())
        write_result = self._fs.upload_file(file_name=new_file_name, bucket=bucket_name, file=uploaded_file)

        # respond_dto = UploadingImageResponse(
        output_dto = UploadingImageResponse(
          status=True,
          bucket_name=write_result.bucket_name,
          object_name=str(write_result.object_name),
          location=str(
            write_result.location if write_result.location
            else f"/{write_result.bucket_name}/{write_result.object_name}"
          )
        )
        self._ob.present(response_dto=output_dto)

        # TODO: write data into database

        uow.commit()
      except Exception as exc:
        raise exc
