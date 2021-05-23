#!/usr/bin/env python
# -*- coding: utf-8 -*-
import uuid
from typing import TYPE_CHECKING

from foundation.entity import Entity
from foundation.events import EventMixin
from product_catalog.domain.rules.display_name_must_not_be_empty_rule import DisplayNameMustNotBeEmptyRule
from product_catalog.domain.rules.product_unit_must_be_in_wellformed_rule import ProductUnitMustBeInWellformedRule
from product_catalog.domain.rules.reference_must_not_be_empty_rule import ReferenceMustNotBeEmptyRule
from product_catalog.domain.value_objects import ProductId

if TYPE_CHECKING:
    from product_catalog.domain.entities.catalog import Catalog
    from product_catalog.domain.entities.collection import Collection


class Product(EventMixin, Entity):
    def __init__(
            self,
            product_id: ProductId,
            reference: str,
            display_name: str,
            collection=None,
            catalog=None,
    ):
        super().__init__()

        self.check_rule(ReferenceMustNotBeEmptyRule(reference=reference))
        self.check_rule(DisplayNameMustNotBeEmptyRule(dn=display_name))

        self._product_id = product_id
        self._reference = reference
        self.display_name = display_name

        # setup other fields
        self._units = []

        # set collection and catalog data
        if collection:
            self._collection = collection  # type: Collection
            self._collection_reference = collection.reference

        if catalog:
            self._catalog = catalog  # type: Catalog
            self._catalog_reference = catalog.reference

    @property
    def product_id(self):
        return self._product_id

    @property
    def reference(self):
        return self._reference

    @property
    def collection(self):
        return self._collection

    @property
    def catalog(self):
        return self._catalog

    @property
    def units(self):
        return self._units;

    @staticmethod
    def create(
            reference: str,
            display_name: str,
            **kwargs
    ):
        product = Product(
            product_id=ProductId(uuid.uuid4()),
            reference=reference,
            display_name=display_name
        )

        return product

    def add_unit(
            self,
            product_unit: ProductUnit
    ):
        product_unit.default = True if not self.has_any_unit() else False

        # check rules
        self.check_rule(ProductUnitMustBeInWellformedRule(product_unit=product_unit))
        self.check_rule(ProductUnitMustBeDefaultIfProductHasNoRule(product_unit=product_unit, units=self.units))
        self.check_rule(ProductMustNotContainAddingUnitRule(adding_unit=product_unit.unit, units=self.units))

        if not product_unit.default:
            base_unit = product_unit.base.unit

            self.check_rule(UnitWithSameConfigurationHasBeenExistedRule(
                product_id=self.product_id,
                multiplier=product_unit.multiplier_to_base,
                base_unit=product_unit.base.unit,
            ))
            self.check_rule(ProductMustHaveBaseUnitRule(unit=base_unit, units=self.units))
            self.check_rule(UnitMustBeCalculatedToDefaultUnit(unit=base_unit, units=self.units))

        # set the updated_at for tracking the version of `ProductConversion` that will be created later in the event
        # handling job
        self._units.add(product_unit)

        # set the updated_time via `DomainEventBase._occured_on`
        self.add_domain_event(ProductUnitCreatedEvent(
            product_id=self.product_id,
            unit=product_unit.unit,
            occured_on=updated_time
        ))

    def has_any_unit(self):
        raise NotImplementedError
