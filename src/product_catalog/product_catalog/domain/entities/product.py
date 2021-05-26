#!/usr/bin/env python
# -*- coding: utf-8 -*-
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Set, Optional

from foundation.entity import Entity
from foundation.events import EventMixin
from product_catalog.domain.entities.product_unit import ProductUnit
from product_catalog.domain.events.product_unit_created_event import ProductUnitCreatedEvent
from product_catalog.domain.rules.display_name_must_not_be_empty_rule import DisplayNameMustNotBeEmptyRule
from product_catalog.domain.rules.product_must_have_base_unit_rule import ProductMustHaveBaseUnitRule
from product_catalog.domain.rules.product_unit_must_be_in_wellformed_rule import ProductUnitMustBeInWellformedRule
from product_catalog.domain.rules.reference_must_not_be_empty_rule import ReferenceMustNotBeEmptyRule
from product_catalog.domain.rules.unit_must_be_calculated_to_default_unit_rule import \
    UnitMustBeCalculatedToDefaultUnitRule
from product_catalog.domain.rules.unit_with_same_configuration_has_been_existed_rule import \
    UnitWithSameConfigurationHasBeenExistedRule
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
        self._units = set()

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
    def units(self) -> Set[ProductUnit]:
        return self._units

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

        if not product_unit.default:
            base_unit = self.get_base_unit_of(product_unit)

            self.check_rule(UnitWithSameConfigurationHasBeenExistedRule(product=self, product_unit=product_unit))
            self.check_rule(ProductMustHaveBaseUnitRule(product=self, base_unit=product_unit.base_unit))
            self.check_rule(UnitMustBeCalculatedToDefaultUnitRule(product=self, product_unit=product_unit))

        # set the updated_at for tracking the version of `ProductConversion` that will be created later in the event
        # handling job
        self._units.add(product_unit)

        # set the updated_time via `DomainEventBase._occured_on`
        self._record_event(ProductUnitCreatedEvent(
            product_id=self.product_id,
            unit=product_unit.unit,
            occured_on=datetime.now()
        ))

    def set_default_unit(
            self,
            product_unit: ProductUnit
    ):
        if product_unit in self._units:
            for u in self._units:
                if u == product_unit:
                    u.default = True

    def has_any_unit(self) -> bool:
        """
        Return if this product has any unit or not

        :return: True if contains unit, else False
        """
        return len(self._units) > 0

    def get_unit_by_name(self, unit: str) -> Optional[ProductUnit]:
        """
        Search and return the product unit by its name

        :param unit: unit name, in string
        :return: an instance of ProductUnit if found, else None
        """
        try:
            u = next(u for u in self.units if u.unit == unit)
            return u
        except StopIteration:
            return None

    def get_base_unit_of(self, product_unit: ProductUnit) -> Optional[ProductUnit]:
        """
        Return a base_unit of an unit

        :param product_unit:
        :return:
        """
        if type(product_unit.base_unit) is ProductUnit:
            return product_unit.base_unit  # type: ignore
        elif type(product_unit.base_unit) is str:
            try:
                u = next(u for u in self.units if u.unit == product_unit.base_unit)
                return u
            except StopIteration:
                return None
        else:
            return None
