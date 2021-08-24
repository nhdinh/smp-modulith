#!/usr/bin/env python
# -*- coding: utf-8 -*-
from web_app.blueprints.shop.shop_bp import shop_blueprint, ShopAPI
from web_app.blueprints.shop.shop_catalog_bp import ShopCatalogAPI, shop_catalog_blueprint
from web_app.blueprints.shop.shop_product_bp import ShopProductAPI, shop_product_blueprint
from web_app.blueprints.shop.shop_supplier_bp import ShopSupplierAPI, shop_supplier_blueprint
from web_app.blueprints.shop.shop_brand_bp import ShopBrandAPI, shop_brand_blueprint

__all__ = [
    shop_blueprint, shop_catalog_blueprint, shop_supplier_blueprint, shop_product_blueprint, shop_brand_blueprint,
    ShopAPI, ShopCatalogAPI, ShopProductAPI, ShopSupplierAPI, ShopBrandAPI,
]
