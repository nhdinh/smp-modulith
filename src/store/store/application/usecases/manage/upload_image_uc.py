#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import uuid
from dataclasses import dataclass
from pathlib import Path
from sys import path
from typing import Optional

from marshmallow import fields
from minio import Minio
from minio.helpers import ObjectWriteResult
from werkzeug.datastructures import FileStorage

from db_infrastructure import GUID
from store.application.services.store_unit_of_work import StoreUnitOfWork
from store.application.usecases.const import ExceptionMessages

from store.application.usecases.store_uc_common import GenericStoreResponseBoundary, fetch_store_by_owner_or_raise, \
    GenericStoreActionResponse

ALLOWED_EXTENSIONS = {'image/jpg', 'image/jpeg', 'image/png'}


@dataclass
class UploadingImageRequest:
    current_user: str
    # file: fields.Raw(type='file')
    upload_for: Optional[str] = ''
    identity: Optional[str] = ''


@dataclass()
class UploadingImageResponse:
    status: bool


class UploadImageUC:
    def __init__(self, ob: GenericStoreResponseBoundary, uow: StoreUnitOfWork, minio_client: Minio):
        self._ob = ob
        self._uow = uow
        self._minio = minio_client

    def execute(self, uploaded_file: FileStorage, dto: UploadingImageRequest):
        with self._uow as uow:  # type:StoreUnitOfWork
            try:
                store = fetch_store_by_owner_or_raise(store_owner=dto.current_user, uow=uow)

                # validate allowed file extension
                if uploaded_file.content_type not in ALLOWED_EXTENSIONS:
                    raise Exception(ExceptionMessages.INVALID_FILE_TYPE)

                # validate file size

                # generate new file name
                upload_for = dto.upload_for if dto.upload_for else 'unassigned'
                identity = str(dto.identity) if dto.identity else str(uuid.uuid4())
                file_ext = Path(uploaded_file.filename).suffix
                new_file_name = f"{upload_for}_{identity}{file_ext}"
                file_size = os.fstat(uploaded_file.fileno()).st_size

                # get bucket
                bucket_name = str(store.store_id)
                default_bucket_policy = policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"AWS": "*"},
                            "Action": ["s3:GetBucketLocation", "s3:ListBucket"],
                            "Resource": f"arn:aws:s3:::{bucket_name}",
                        },
                        {
                            "Effect": "Allow",
                            "Principal": {"AWS": "*"},
                            "Action": "s3:GetObject",
                            "Resource": f"arn:aws:s3:::{bucket_name}/*",
                        },
                    ],
                }
                if not self._minio.bucket_exists(bucket_name=bucket_name):
                    self._minio.make_bucket(bucket_name=bucket_name)
                    self._minio.set_bucket_policy(bucket_name=bucket_name, policy=json.dumps(default_bucket_policy))

                # upload image
                # write_result = self._minio.fput_object(bucket_name, new_file_name,
                #                                        uploaded_file)  # type: ObjectWriteResult
                write_result = self._minio.put_object(
                    bucket_name=bucket_name,
                    object_name=new_file_name,
                    data=uploaded_file, length=file_size,
                    content_type=uploaded_file.content_type)  # type: ObjectWriteResult

                # respond_dto = UploadingImageResponse(
                response_dto = GenericStoreActionResponse(
                    status=True
                )
                self._ob.present(dto=response_dto)

                uow.commit()
            except Exception as exc:
                raise exc
