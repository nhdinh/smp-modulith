#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector
from minio import Minio

from foundation.fs import FileSystem
from shop.application.usecases.shop.upload_image_uc import UploadingImageResponseBoundary, UploadImageUC


class FoundationApplicationModule(injector.Module):
    @injector.provider
    def upload_image_uc(self, boundary: UploadingImageResponseBoundary, uow, minio_client: Minio,
                        fs: FileSystem) -> UploadImageUC:
        return UploadImageUC(boundary, uow, minio_client, fs)
