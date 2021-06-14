#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass, field
from typing import Optional, List

from sqlalchemy.orm import Session

from foundation import slugify
from product_catalog import CatalogUnitOfWork
from product_catalog.domain.entities.brand import Brand
from product_catalog.domain.entities.catalog import Catalog
from product_catalog.domain.entities.collection import Collection
from product_catalog.domain.entities.product import Product
from product_catalog.domain.entities.product_unit import ProductUnit, DEFAULT_UNIT_CONVERSION_MULTIPLIER_FACTOR
from product_catalog.domain.value_objects import ProductReference, CatalogReference, CollectionReference


@dataclass(frozen=True)
class CreatingUnitConversionRequest:
    unit: str
    multiplier: float


@dataclass(frozen=True)
class CreatingFirstStockingRequest:
    unit: str
    stocking: float


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

    def execute(self, dto: CreatingProductRequest):
        with self._uow as uow:
            try:
                # find catalog
                catalog = CreateProductUC.get_catalog_or_return_default(
                    uow=uow,
                    catalog_display_name=dto.catalog_display_name,
                    catalog_reference=dto.catalog_reference
                )

                # find or create collection
                collection = CreateProductUC.get_collection_or_return_default(
                    catalog=catalog,
                    collection_display_name=dto.collection_display_name,
                    collection_reference=dto.collection_reference
                )

                # create product
                product_reference = dto.reference
                display_name = dto.display_name

                # make product_reference
                product_reference = product_reference if product_reference else slugify(display_name)
                product = catalog.create_product(
                    reference=product_reference,
                    display_name=display_name,
                    collection=collection,
                    sku=dto.sku,
                    barcode=dto.barcode,
                )  # type:Product

                # add unit
                default_unit = None
                if dto.default_unit:
                    default_unit = ProductUnit(unit=dto.default_unit, base_unit=None,
                                               multiplier=DEFAULT_UNIT_CONVERSION_MULTIPLIER_FACTOR,
                                               default=True)
                    product.add_unit(default_unit)

                unit_conversions = CreateProductUC.clean_unit_conversions_input(dto.unit_conversions)
                if len(unit_conversions):
                    if not default_unit:
                        raise Exception('Default Unit must be setted before creating more unit')

                    for unit_conversion in unit_conversions:
                        product_unit = ProductUnit(unit=unit_conversion.unit, base_unit=default_unit.unit,
                                                   multiplier=unit_conversion.multiplier, default=False)
                        product.add_unit(product_unit)

                # with brand?
                brand_display_name, brand_reference = dto.brand_display_name, dto.brand_reference
                brand = self.get_brand_or_return_default(brand_display_name=brand_display_name,
                                                         brand_reference=brand_reference)
                product._brand = brand

                # output dto
                output_dto = CreatingProductResponse(product_id=str(product.product_id), reference=product.reference)
                self._ob.present(output_dto)

                uow.commit()
            except Exception as exc:
                raise exc

    @classmethod
    def get_catalog_or_return_default(cls,
                                      uow: CatalogUnitOfWork,
                                      catalog_display_name='Default Catalog',
                                      catalog_reference='default_catalog') -> Catalog:
        # rebuild catalog_reference
        if catalog_reference == 'default_catalog' and catalog_display_name != 'Default Catalog':
            catalog_reference = slugify(catalog_display_name)

        if not catalog_reference and not catalog_display_name:
            catalog_display_name = 'Default Catalog'
            catalog_reference = 'default_catalog'

        if catalog_display_name:
            catalog_reference = catalog_reference if catalog_reference else slugify(catalog_display_name)

        # trying to get catalog from persisted data
        catalog = uow.catalogs.get(reference=catalog_reference)
        if catalog:
            # if catalog_display_name is None, then return immediately as there is no need to comparison
            if not catalog_display_name:
                return catalog

            # else, compare with the display_name to see if it matches
            if catalog.display_name == catalog_display_name:
                return catalog
            else:
                raise Exception(f'Cannot create Catalog. Catalog with reference={catalog_reference} existed.')

        # If there is an input of brand_reference, then we will check the database first for the existing brand.
        # If there is no such brand exists, then we will create one
        if not catalog:
            # need to create one
            catalog = Catalog.create(reference=catalog_reference, display_name=catalog_display_name)
            uow.catalogs.save(catalog)

        return catalog

    @classmethod
    def get_collection_or_return_default(
            cls,
            catalog: Catalog,
            collection_display_name='Default Collection',
            collection_reference='default_collection'
    ) -> Collection:
        """
        Get collection from persisted data or create new one based on inputs. Else get/ create a default one

        :param catalog:
        :param collection_display_name:
        :param collection_reference:
        :return:
        """
        # manipulate input
        if collection_reference == 'default_collection' and collection_display_name != 'Default Collection':
            collection_reference = slugify(collection_display_name)

        if not collection_reference and not collection_display_name:
            collection_reference = 'default_collection'
            collection_display_name = 'Default Collection'

        if collection_display_name:
            collection_reference = collection_reference if collection_reference else slugify(collection_display_name)

        # search collection in catalog
        try:
            collection = next(c for c in catalog.collections if c.reference == collection_reference)
            if collection:
                if not collection_display_name:
                    return collection

                if collection.display_name == collection_display_name:
                    return collection
                else:
                    raise Exception(
                        f'Cannot create Collection. Collection with reference={collection_reference} existed.')
        except StopIteration:
            collection = None
        except Exception as exc:
            raise exc

        # get from persisted
        collection = catalog.create_child_collection(collection_reference=collection_reference,
                                                     display_name=collection_display_name,
                                                     set_default=collection_reference == 'default_collection')

        return collection

    def get_brand_or_return_default(
            self,
            brand_display_name: str = 'Default Brand',
            brand_reference: str = 'default_brand'
    ) -> Brand:
        """
        Get a brand from persisted data by its display_name and reference. If not persisted, then create it. Or if
        there is no input data, then get the default one

        :param brand_display_name: display_name of a brand
        :param brand_reference:  reference of a brand
        :return: brand instance
        """
        # manipulate brand input
        if brand_reference == 'default_brand' and brand_display_name != 'Default Brand':
            brand_reference = slugify(brand_display_name)

        if not brand_reference and not brand_display_name:
            brand_reference = 'default_brand'
            brand_display_name = 'Default Brand'

        if brand_display_name:
            brand_reference = brand_reference if brand_reference else slugify(brand_display_name)

        # If there is an input of brand_reference, then we will check the database first for the existing brand.
        # If there is no such brand exists, then we will create one
        current_session = self._uow.session  # type:Session
        brand = current_session.query(Brand).filter(Brand.reference == brand_reference).first()
        if not brand:
            # need to create one
            brand = Brand(reference=brand_reference, display_name=brand_display_name)

        if brand_display_name:
            if brand.display_name != brand_display_name:
                raise Exception(f'Cannot create Brand. Brand with reference={brand} existed.')

        return brand

    @classmethod
    def clean_unit_conversions_input(cls, unit_conversions):
        """
        Clean the input data

        :param unit_conversions: input data of unit conversions in dto
        """
        ret = []
        for conv in unit_conversions:
            if conv.unit and conv.multiplier > 0:
                ret.append(conv)

        return ret
