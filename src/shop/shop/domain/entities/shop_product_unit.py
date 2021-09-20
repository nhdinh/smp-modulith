#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from shop.domain.entities.value_objects import ExceptionMessages

MAX_RECURSION = 12


@dataclass
class ShopProductUnit:
    unit_name: str
    conversion_factor: float = 0
    default: bool = False
    disabled: bool = False
    referenced_unit: Optional[ShopProductUnit] = None
    deleted: bool = False

    def calculate_conversion_factor_to_default_unit(self) -> Tuple[float, ShopProductUnit]:
        """
        Calculate and return the conversion_factor of this ShopProductUnit against the default unit. This method will
        calculate with maximum recursion = 12. If the recursion is too high, mean that there are alot of unit that
        referenced to the another, in chaining. The maximun number of chaining reference is 12.

        :return: a tuple of conversion factor and default unit
        """
        # return 1 if self is default unit
        if self.default:
            return 1, self

        # else
        recursion_time = 1
        conversion_factor = self.conversion_factor
        ref_unit = self.referenced_unit

        while not ref_unit.default and recursion_time <= MAX_RECURSION:
            conversion_factor *= ref_unit.conversion_factor
            ref_unit = ref_unit.referenced_unit
            recursion_time += 1

        if ref_unit.default:
            return conversion_factor, ref_unit
        else:
            raise RecursionError()

    def __eq__(self, other):
        if not other or not isinstance(other, ShopProductUnit):
            raise TypeError(ExceptionMessages.WRONG_DATA_TYPE_TO_COMPARE)

        if getattr(self, '_product', None) is not None and getattr(other, '_product', None) is not None:
            return self._product == other._product \
                   and self.conversion_factor == other.conversion_factor \
                   and self.referenced_unit == other.referenced_unit
        else:
            return self.conversion_factor == other.conversion_factor \
                   and self.referenced_unit == other.referenced_unit

    def __hash__(self):
        h = hash((getattr(self, '_product'), self.conversion_factor, self.referenced_unit.__hash__()))
        return h

    def __truediv__(self, other):
        the_and_of_something = getattr(self, '_product', None) is not None \
                               and getattr(other, '_product', None) is not None \
                               and getattr(self, '_product') != getattr(other, '_product')

        if not other \
                or not isinstance(other, ShopProductUnit) \
                or the_and_of_something:
            raise TypeError(ExceptionMessages.WRONG_DATA_TYPE_TO_OPERATE)

        self_factor, self_default_unit = self.calculate_conversion_factor_to_default_unit()
        other_factor, other_default_unit = other.calculate_conversion_factor_to_default_unit()

        if self_default_unit == other_default_unit:
            return self_factor.__truediv__(other_factor)
        else:
            raise TypeError(ExceptionMessages.WRONG_DATA_TYPE_TO_OPERATE)

    def __mul__(self, other: int):
        if not isinstance(other, int):
            raise TypeError(ExceptionMessages.WRONG_DATA_TYPE_TO_OPERATE)

        self.conversion_factor *= other
        return self
