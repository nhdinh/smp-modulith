#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os

from minio import Minio
from minio.helpers import ObjectWriteResult
from werkzeug.datastructures import FileStorage

from foundation.common_helpers import slugify, AWS_ALLOWED_SEPARATOR


def default_bucket_policy(bucket_name: str):
  return {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Action": [
          "s3:GetObject",
          "s3:GetBucketLocation",
        ],
        "Effect": "Allow",
        "Principal": '*',
        "Resource": [
          f"arn:aws:s3:::{bucket_name}",
          f"arn:aws:s3:::{bucket_name}/*"
        ],
        "Sid": "Public"
      }
    ]
  }


class FileSystem:
  def __init__(self, minio: Minio):
    self._minio = minio

  def upload_file(self, file_name: str, bucket: str, file: FileStorage) -> ObjectWriteResult:
    try:
      bucket = slugify(bucket).replace('.', AWS_ALLOWED_SEPARATOR)
      if not self._minio.bucket_exists(bucket_name=bucket):
        self._minio.make_bucket(bucket_name=bucket)
        self._minio.set_bucket_policy(bucket_name=bucket,
                                      policy=json.dumps(default_bucket_policy(bucket_name=bucket)))

      file_size = os.fstat(file.fileno()).st_size

      write_result = self._minio.put_object(
        bucket_name=bucket,
        object_name=file_name,
        data=file, length=file_size,
        content_type=file.content_type,
      )  # type: ObjectWriteResult

      return write_result
    except Exception as exc:
      raise exc
