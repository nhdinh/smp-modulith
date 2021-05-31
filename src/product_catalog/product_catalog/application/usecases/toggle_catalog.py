#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from product_catalog import CatalogUnitOfWork


@dataclass
class TogglingCatalogResponse:
    reference: str
    disabled: bool


class TogglingCatalogResponseBoundary(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def present(self, response_dto: TogglingCatalogResponse) -> None:
        raise NotImplementedError


class ToggleCatalogUC:
    def __init__(self,
                 output_boundary: TogglingCatalogResponseBoundary,
                 uow: CatalogUnitOfWork) -> None:
        self._ob = output_boundary
        self._uow = uow

    def execute(self, catalog_reference: str) -> None:
        with self._uow as uow:  # type: CatalogUnitOfWork
            try:
                catalog = uow.catalogs.get(reference=catalog_reference)
                if not catalog:
                    raise Exception('Catalog not found')

                if catalog.system:
                    raise Exception('Cannot change status of system catalog')

                catalog.disabled = not catalog.disabled

                # output dto
                output_dto = TogglingCatalogResponse(reference=catalog.reference, disabled=catalog.disabled)
                self._ob.present(output_dto)

                uow.commit()
            except Exception as exc:
                raise exc
