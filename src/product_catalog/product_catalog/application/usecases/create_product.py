#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from typing import Optional

from slugify import slugify
from sqlalchemy.orm import Session

from product_catalog import CatalogUnitOfWork
from product_catalog.domain.entities.brand import Brand
from product_catalog.domain.entities.catalog import Catalog
from product_catalog.domain.entities.collection import Collection
from product_catalog.domain.entities.product import Product
from product_catalog.domain.value_objects import ProductReference, CatalogReference, CollectionReference


@dataclass
class CreatingProductRequest:
    display_name: str
    reference: Optional[ProductReference] = None
    catalog_reference: Optional[CatalogReference] = None
    catalog_display_name: Optional[str] = None
    collection_reference: Optional[CollectionReference] = None
    collection_display_name: Optional[str] = None
    brand_reference: Optional[str] = None
    brand_display_name: Optional[str] = None


@dataclass
class CreatingProductResponse:
    product_id: str
    reference: str


class CreatingProductResponseBoundary(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def present(self, response_dto: CreatingProductResponse) -> None:
        raise NotImplementedError


class CreateProductUC:
    def __init__(self,
                 output_boundary: CreatingProductResponseBoundary,
                 uow: CatalogUnitOfWork) -> None:
        self._ob = output_boundary
        self._uow = uow

    def get_or_create_catalog(
            self,
            catalog_display_name: Optional[str] = None,
            catalog_reference: Optional[str] = None
    ) -> Catalog:
        """
        Fetch a catalog from database or create a new one with specified input data

        :param catalog_display_name: display name of the catalog
        :param catalog_reference: reference string of the catalog
        """
        pass

    def get_or_create_brand(
            self,
            brand_display_name: Optional[str] = None,
            brand_reference: Optional[str] = None,
    ) -> Optional[Brand]:
        brand_reference = brand_reference if brand_reference else slugify(brand_display_name)

        # if there is no reference input, then return None
        if not brand_reference:
            return None

        # If there is an input of brand_reference, then we will check the database first for the existing brand.
        # If there is no such brand exists, then we will create one
        current_session = self._uow.session  # type:Session
        brand = current_session.query(Brand).filter(Brand.reference == brand_reference).first()
        if not brand:
            # need to create one
            brand = Brand(reference=brand_reference, display_name=brand_display_name)

        return brand

    def execute(self, product_dto: CreatingProductRequest):
        with self._uow as uow:
            try:
                # find catalog
                catalog: Optional[Catalog] = None
                new_catalog_created = False
                catalog_reference = product_dto.catalog_reference \
                    if product_dto.catalog_reference else slugify(product_dto.catalog_display_name)
                if catalog_reference:
                    catalog = uow.catalogs.get(reference=catalog_reference)

                if not catalog:
                    catalog_display_name = product_dto.catalog_display_name
                    if catalog_display_name:
                        _slugified_catalog_reference = slugify(
                            catalog_display_name) if not catalog_reference else catalog_reference
                        catalog = uow.catalogs.get(reference=_slugified_catalog_reference)
                        if not catalog:
                            catalog = Catalog.create(reference=_slugified_catalog_reference,
                                                     display_name=catalog_display_name)
                            uow.catalogs.save(catalog)
                            new_catalog_created = True
                    else:  # no reference and no display_name
                        catalog = uow.catalogs.get_default_catalog()

                # find collection
                collection: Optional[Collection] = None
                collection_display_name = product_dto.collection_display_name
                collection_reference = product_dto.collection_reference \
                    if product_dto.collection_reference else slugify(collection_display_name)
                if new_catalog_created:
                    # create new collection
                    collection_reference = collection_reference \
                        if collection_reference else slugify(collection_display_name)
                    collection = catalog.create_child_collection(collection_reference=collection_reference,
                                                                 display_name=collection_display_name,
                                                                 set_default=True)
                else:
                    # old catalog, find the collection
                    if collection_reference:
                        try:
                            collection = next(c for c in catalog.collections.__iter__()
                                              if c.reference == collection_reference)
                        except StopIteration:
                            pass

                    # still no collection with specified reference, check again with display name
                    if not collection:
                        if collection_display_name:
                            _slugified_collection_reference = slugify(
                                collection_display_name) if not collection_reference else collection_reference
                            collection = catalog.create_child_collection(
                                collection_reference=_slugified_collection_reference,
                                display_name=collection_display_name)
                        else:
                            # no collection reference as well as no collection display name is provide, so get teh
                            # default collection
                            if len(catalog.collections) == 0:
                                collection = catalog.create_child_collection(collection_reference='default_collection',
                                                                             display_name='Default Collection',
                                                                             set_default=True)
                            else:
                                collection = catalog.default_collection

                product_reference = product_dto.reference
                display_name = product_dto.display_name

                # make product_reference
                product_reference = product_reference if product_reference else slugify(display_name)

                product = catalog.create_product(
                    reference=product_reference,
                    display_name=display_name,
                    collection=collection,
                )  # type:Product

                # with brand?
                if product_dto.brand_display_name or product_dto.brand_reference:
                    brand = self.get_or_create_brand(
                        brand_display_name=product_dto.brand_display_name,
                        brand_reference=product_dto.brand_reference
                    )
                    product._brand = brand

                # output dto
                output_dto = CreatingProductResponse(product_id=str(product.product_id), reference=product.reference)
                self._ob.present(output_dto)

                uow.commit()
            except Exception as exc:
                raise exc
