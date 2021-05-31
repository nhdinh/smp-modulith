#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from product_catalog import CatalogUnitOfWork


@dataclass
class DeletingCatalogResponse:
    reference: str
    deleted: bool


class DeletingCatalogResponseBoundary(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def present(self, response_dto: DeletingCatalogResponse):
        raise NotImplementedError


class DeleteCatalogUC:
    def __init__(self,
                 ob: DeletingCatalogResponseBoundary,
                 uow: CatalogUnitOfWork):
        self._ob = ob
        self._uow = uow

    def execute(self, catalog_reference: str, delete_product: bool = False) -> None:
        with self._uow as uow:  # type:CatalogUnitOfWork
            try:
                catalog = uow.catalogs.get(reference=catalog_reference)
                if not catalog:
                    raise Exception('Catalog not found')

                if catalog.system:
                    raise Exception('Cannot delete a system catalog')

                system_catalog = uow.catalogs.get_default_catalog()
                default_collection = system_catalog.default_collection

                collections = list(catalog.collections)
                for collection in collections:
                    products = list(collection.products)

                    if not delete_product:
                        # move product to system catalog
                        default_collection.products.update(products)
                    else:
                        for product in products:
                            uow.session.delete(product)

                    # remove collection
                    uow.session.delete(collection)

                # delete catalog
                uow.session.delete(catalog)
                uow.commit()

                # output dto
                output_dto = DeletingCatalogResponse(reference=catalog_reference, deleted=True)
                self._ob.present(output_dto)
            except Exception as exc:
                raise exc
