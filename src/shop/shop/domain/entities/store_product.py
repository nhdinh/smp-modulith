#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, TYPE_CHECKING, Set, List, Tuple, Dict

from foundation.entity import Entity
from foundation.events import EventMixin, ThingGoneInBlackHoleError
from foundation.value_objects import Money
from foundation.value_objects.factories import get_money
from shop.adapter.id_generators import generate_product_id
from shop.domain.entities.purchase_price import ProductPurchasePrice
from shop.domain.entities.shop_supplier import ShopSupplier
from shop.domain.entities.shop_unit import ShopProductUnit
from shop.domain.entities.store_product_brand import ShopProductBrand
from shop.domain.entities.store_product_tag import ShopProductTag
from shop.domain.entities.value_objects import ShopProductId, ExceptionMessages
from shop.domain.rules.thresholds_require_unit_setup_rule import ThresholdsRequireUnitSetupRule


class ShopProduct(EventMixin, Entity):
    product_id: ShopProductId
    title: str

    def __init__(
            self,
            product_id: ShopProductId,
            title: str,
            sku: str,
            image: str,
            shop: 'Shop',
            brand: ShopProductBrand,
            collections: Set['ShopCollection'],
            catalog: 'ShopCatalog',
            default_unit: str,
            suppliers: Set['ShopSupplier'],
            restock_threshold: int = -1,
            max_stock_threshold: int = -1,
    ):
        super(ShopProduct, self).__init__()

        self.check_rule(ThresholdsRequireUnitSetupRule(restock_threshold, max_stock_threshold, default_unit))

        self.product_id = product_id
        self.title = title
        self.sku = sku
        self.barcode = 'NoBarCode applied yet'

        self._shop = shop  # type:Shop
        self.image = image

        self._brand = brand  # type:ShopProductBrand

        self._catalog = catalog  # type:ShopCatalog
        self._collections = collections  # type:Set[ShopCollection]

        self._units = set()  # type:Set[ShopProductUnit]
        self._tags = set()  # type:Set[ShopProductTag]

        # create default unit
        _default_unit = self.create_default_unit(default_name=default_unit)
        self._units.add(_default_unit)

        # add suppliers and price
        self._suppliers = suppliers
        self._purchase_prices = set()  # type:Set[ProductPurchasePrice]

        # thresholds
        self.restock_threshold = restock_threshold
        self.max_stock_threshold = max_stock_threshold

    @classmethod
    def create_product(
            cls,
            title: str,
            sku: str,
            image: str,
            default_unit: str,
            restock_threshold: int,
            max_stock_threshold: int,
            store: 'Shop',
            brand: ShopProductBrand,
            catalog: 'ShopCatalog',
            collections: List['ShopCollection'],
            suppliers: List['ShopSupplier'],
            tags: List[str]
    ) -> 'ShopProduct':
        product_id = generate_product_id()

        product = ShopProduct(
            product_id=product_id,
            title=title,
            sku=sku,
            image=image,
            shop=store,
            brand=brand,
            catalog=catalog,
            collections=set(collections),
            suppliers=set(suppliers),
            default_unit=default_unit,
            restock_threshold=restock_threshold,
            max_stock_threshold=max_stock_threshold,
        )

        # add tags
        if tags:
            for tag in tags:
                product._tags.add(ShopProductTag(tag=tag))

        # add collections
        if collections:
            pass

        return product

    @property
    def catalog(self) -> 'ShopCatalog':
        return self._catalog

    @property
    def collections(self) -> Set['ShopCollection']:
        return self._collections

    @property
    def brand(self) -> 'ShopProductBrand':
        return self._brand

    @brand.setter
    def brand(self, value):
        self._brand = value

    @property
    def suppliers(self) -> Set['ShopSupplier']:
        return self._suppliers

    @property
    def units(self) -> Set[ShopProductUnit]:
        return self._units

    @property
    def default_unit(self) -> ShopProductUnit:
        return self.get_default_unit()

    @property
    def tags(self) -> Set[ShopProductTag]:
        return self._tags

    def is_belong_to_store(self, store: 'Shop') -> bool:
        return self._shop is store

    def get_unit(self, unit: str) -> Optional[ShopProductUnit]:
        try:
            return next(product_unit for product_unit in self._units if product_unit.unit_name == unit)
        except StopIteration:
            return None

    def get_default_unit(self) -> Optional[ShopProductUnit]:
        try:
            return next(product_unit for product_unit in self._units if product_unit.default)
        except StopIteration:
            return None

    def try_to_make_unit(self, unit: str, base_unit: str, conversion_factor: float):
        try:
            _base_unit = self.get_unit(base_unit)
            if not _base_unit:
                raise ThingGoneInBlackHoleError(ExceptionMessages.PRODUCT_UNIT_NOT_FOUND)

            product_unit = ShopProductUnit(unit=unit, from_unit=_base_unit, conversion_factor=conversion_factor)
            # product_unit.product = self
            return product_unit
        except Exception as exc:
            raise exc

    def delete_unit(self, unit: str):
        try:
            unit_to_delete = self.get_unit(unit=unit)
            if not unit_to_delete:
                raise ThingGoneInBlackHoleError(ExceptionMessages.PRODUCT_UNIT_NOT_FOUND)

            # else, check if can be deleted
            can_be_delete = True
            for product_unit in self._units:
                if product_unit.base_unit == unit_to_delete:
                    can_be_delete = False

            if can_be_delete:
                self._units.remove(unit_to_delete)
            else:
                raise Exception(ExceptionMessages.CANNOT_DELETE_DEPENDENCY_PRODUCT_UNIT)
        except Exception as exc:
            raise exc

    def create_unit(self, unit_name: str, conversion_factor: float, base_unit: str = None) -> ShopProductUnit:
        try:
            # check if there is any unit with that name has been existed
            unit = next(unit for unit in self._units if unit.unit_name == unit_name)
            if unit:
                raise Exception(ExceptionMessages.PRODUCT_UNIT_EXISTED)
        except StopIteration:
            pass

        try:
            # indicate if the unit to be created is default unit or not
            if base_unit:
                is_default = False
            else:
                is_default = True

            # search for the unit to be base_unit
            if base_unit:
                _base_unit = next(unit for unit in self._units if unit.unit_name == base_unit)
            else:
                _base_unit = None

            # make unit
            unit = ShopProductUnit(unit_name=unit_name, conversion_factor=conversion_factor, default=is_default,
                                   disabled=False, referenced_unit=_base_unit)
            self._units.add(unit)
            return unit
        except StopIteration:
            raise ThingGoneInBlackHoleError(ExceptionMessages.PRODUCT_BASE_UNIT_NOT_FOUND)

    def create_default_unit(self, default_name: str) -> ShopProductUnit:
        return self.create_unit(unit_name=default_name, conversion_factor=0, base_unit=None)

    def _is_unit_dependency(self, unit: ShopProductUnit):
        try:
            unit = next(u for u in self._units if u.base_unit == unit)
            if unit:
                return True
        except StopIteration:
            return False

    def remove_unit(self, unit_name: str):
        unit = self.get_unit(unit=unit_name)
        if not unit:
            raise ThingGoneInBlackHoleError(ExceptionMessages.PRODUCT_UNIT_NOT_FOUND)
        elif unit.default and len(self._units) > 1:
            raise Exception(ExceptionMessages.CANNOT_DELETE_DEFAULT_UNIT)
        elif self._is_unit_dependency(unit):
            raise Exception(ExceptionMessages.CANNOT_DELETE_DEPENDENCY_PRODUCT_UNIT)
        else:
            unit.deleted = True

    def __repr__(self):
        return f'<StoreProduct ref={self.reference}>'

    def create_purchase_price_by_supplier(self, **kwargs):
        supplier = kwargs.get('supplier')
        unit = kwargs.get('unit')

        price = kwargs.get('price')

        if not isinstance(price, Money):
            try:
                price = Decimal(price).normalize()

                currency = kwargs.get('currency')
                price = get_money(amount=price, currency_str=currency)
            except:
                raise TypeError()

        if supplier in self._suppliers and unit in self._units:
            purchase_price = ProductPurchasePrice(
                supplier=supplier,
                product_unit=unit,
                price=price,
                tax=kwargs.get('tax'),
                effective_from=kwargs.get('effective_from')
            )

            self._purchase_prices.add(purchase_price)

    def get_price(
            self, by_supplier: ShopSupplier, by_unit: ShopProductUnit
    ) -> Optional[Tuple[Money, Optional[float], date]]:
        try:
            price = next(p for p in self._purchase_prices if
                         p.product_unit == by_unit and p.supplier == by_supplier)  # type:ProductPurchasePrice

            return price.price, price.tax, price.effective_from
        except StopIteration:
            return None

    def get_prices(self, by_supplier: ShopSupplier) -> Dict[str, Tuple[Money, float, datetime]]:
        return_data = dict()

        prices = [p for p in self._purchase_prices if p.supplier == by_supplier]
        if not prices:
            return dict()

        for price in prices:  # type:ProductPurchasePrice
            return_data[price.product_unit.unit_name] = tuple(price.price, price.tax, price.effective_from)
