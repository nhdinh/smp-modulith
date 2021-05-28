#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
import decimal
from dataclasses import dataclass, field
from typing import Optional, List, Tuple

from slugify import slugify
from sqlalchemy.orm import Session

from product_catalog import CatalogUnitOfWork
from product_catalog.domain.entities.brand import Brand
from product_catalog.domain.entities.catalog import Catalog
from product_catalog.domain.entities.collection import Collection
from product_catalog.domain.entities.product import Product
from product_catalog.domain.value_objects import ProductReference, CatalogReference, CollectionReference


@dataclass(frozen=True)
class CreatingUnitConversionRequest:
    unit: str
    multiplier: decimal


@dataclass(frozen=True)
class CreatingFirstStockingRequest:
    unit: str
    stocking: decimal


@dataclass
class CreatingProductRequest:
    display_name: str
    reference: Optional[ProductReference] = None
    catalog_reference: Optional[CatalogReference] = None
    catalog_display_name: Optional[str] = ''
    collection_reference: Optional[CollectionReference] = None
    collection_display_name: Optional[str] = ''
    brand_reference: Optional[str] = None
    brand_display_name: Optional[str] = None

    sku: Optional[str] = None
    barcode: Optional[str] = None
    default_unit: Optional[str] = None
    first_inventory_stock: Optional[int] = 0
    seller: Optional[str] = None
    tags: Optional[List[str]] = None

    unit_conversions: Optional[List[CreatingUnitConversionRequest]] = field(default_factory=list)
    first_stocking: Optional[List[CreatingFirstStockingRequest]] = field(default_factory=list)


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

    def execute(self, product_dto: CreatingProductRequest):
        with self._uow as uow:
            try:
                # find catalog
                catalog: Optional[Catalog] = None
                new_catalog_created = False
                catalog_reference = product_dto.catalog_reference
                catalog_display_name = product_dto.catalog_display_name
                if catalog_reference:
                    catalog = uow.catalogs.get(reference=catalog_reference)

                if not catalog:
                    catalog, new_catalog_created = self.get_catalog_or_return_default(
                        catalog_display_name=catalog_display_name, catalog_reference=catalog_reference)

                # find collection
                collection: Optional[Collection] = None
                collection_display_name = product_dto.collection_display_name
                collection_reference = product_dto.collection_reference
                if new_catalog_created:
                    # create new collection
                    collection = self.get_collection_or_return_default(
                        collection_display_name=collection_display_name, collection_reference=collection_reference)

                    # add collection to catalog
                    catalog.collections.add(collection)
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
                        collection = self.get_collection_or_return_default(
                            collection_display_name=collection_display_name, collection_reference=collection_reference)

                        # add collection to catalog
                        catalog.collections.add(collection)

                # create product
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
                brand_display_name, brand_reference = product_dto.brand_display_name, product_dto.brand_reference
                brand = self.get_brand_or_return_default(brand_display_name=brand_display_name,
                                                         brand_reference=brand_reference)
                product._brand = brand

                # output dto
                output_dto = CreatingProductResponse(product_id=str(product.product_id), reference=product.reference)
                self._ob.present(output_dto)

                uow.commit()
            except Exception as exc:
                raise exc

    def get_catalog_or_return_default(self, catalog_display_name='Default Catalog',
                                      catalog_reference='default_catalog') -> Tuple[Catalog, bool]:
        catalog_reference = catalog_reference if catalog_reference else slugify(catalog_display_name)
        new_created = False

        # if there is no reference input, then return default
        if not catalog_reference:
            catalog_reference = 'default_catalog'  # default catalog_reference
            catalog_display_name = 'Default Catalog'  # default catalog_display_name

        # If there is an input of brand_reference, then we will check the database first for the existing brand.
        # If there is no such brand exists, then we will create one
        current_session = self._uow.session  # type:Session
        catalog = current_session.query(Catalog).filter(Catalog._reference == catalog_reference).first()
        if not catalog:
            # need to create one
            catalog = Brand(reference=catalog_reference, display_name=catalog_display_name)
            new_created = True

        return catalog, new_created

    def get_collection_or_return_default(
            self,
            catalog: Catalog, collection_display_name='Default Collection',
            collection_reference='default_collection'
    ) -> Collection:
        collection_reference = collection_reference if collection_reference else slugify(collection_display_name)

        # no reference, return default
        if not collection_reference:
            collection_reference = 'default_collection'
            collection_display_name = 'Default Collection'

        # get from persisted
        sess = self._uow.session  # type:Session
        collection = sess.query(Collection).filter(Collection._reference == collection_reference).first()
        if not collection:
            # create one
            collection = Collection(reference=collection_reference, display_name=collection_display_name)

        return collection

    def get_brand_or_return_default(
            self,
            brand_display_name: str = 'Default Brand',
            brand_reference: str = 'default_brand'
    ) -> Brand:
        """
        Get a brand from persisted data by its display_name and reference. If not persisted, then create it. Or if there is no input data, then get the default one

        :param brand_display_name: display_name of a brand
        :param brand_reference:  reference of a brand
        :return: brand instance
        """
        brand_reference = brand_reference if brand_reference else slugify(brand_display_name)

        # if there is no reference input, then create default
        if not brand_reference:
            brand_reference = 'default_brand'
            brand_display_name = 'Default Brand'

        # If there is an input of brand_reference, then we will check the database first for the existing brand.
        # If there is no such brand exists, then we will create one
        current_session = self._uow.session  # type:Session
        brand = current_session.query(Brand).filter(Brand.reference == brand_reference).first()
        if not brand:
            # need to create one
            brand = Brand(reference=brand_reference, display_name=brand_display_name)

        return brand
