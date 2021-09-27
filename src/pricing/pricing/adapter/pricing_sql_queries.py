#!/usr/bin/env python
# -*- coding: utf-8 -*-
class SqlGetShopProductPurchasePriceQuery(GetShopProductPurchasePriceQuery, SqlQuery):
    def query(self, dto: GetShopProductPurchasePriceRequest) -> ShopProductPriceDto:
        try:
            valid_shop_id = sql_get_authorized_shop_id(shop_id=dto.shop_id, current_user_id=dto.current_user_id,
                                                       conn=self._conn)
            if not valid_shop_id:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_OWNERSHIP_NOT_FOUND)

            purchase_price_query = list_purchase_prices_bound_to_product_query_factory(shop_id=dto.shop_id,
                                                                                       product_id=dto.product_id) \
                .where(and_(shop_product_purchase_price_table.c.unit_id == shop_product_unit_table.c.unit_id,
                            shop_product_purchase_price_table.c.supplier_id == dto.supplier_id,
                            shop_product_unit_table.c.unit_name == dto.unit))
            price = self._conn.execute(purchase_price_query).first()

            return _row_to_product_price_dto(price) if price else empty_list_response()
        except Exception as exc:
            raise exc


class SqlGetShopProductLowestPurchasePriceQuery(GetShopProductLowestPurchasePriceQuery, SqlQuery):
    def query(self, dto: GetShopProductLowestPurchasePriceRequest) -> ShopProductPriceDto:
        try:
            valid_shop_id = sql_get_authorized_shop_id(shop_id=dto.shop_id, current_user_id=dto.current_user_id,
                                                       conn=self._conn)
            if not valid_shop_id:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_OWNERSHIP_NOT_FOUND)

            purchase_price_query = list_purchase_prices_bound_to_product_query_factory(shop_id=dto.shop_id,
                                                                                       product_id=dto.product_id) \
                .where(and_(shop_product_purchase_price_table.c.unit_id == shop_product_unit_table.c.unit_id,
                            shop_product_unit_table.c.unit_name == dto.unit)) \
                .order_by(asc(shop_product_purchase_price_table.c.price))
            price = self._conn.execute(purchase_price_query).first()

            return _row_to_product_price_dto(price) if price else empty_list_response()
        except Exception as exc:
            raise exc


class SqlListShopProductPurchasePricesQuery(ListShopProductPurchasePricesQuery, SqlQuery):
    def query(self, dto: ListShopProductPurchasePricesRequest) -> SimpleListTypedResponse[ShopProductPriceDto]:
        try:
            valid_shop_id = sql_get_authorized_shop_id(shop_id=dto.shop_id, current_user_id=dto.current_user_id,
                                                       conn=self._conn)
            if not valid_shop_id:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_OWNERSHIP_NOT_FOUND)

            purchase_prices_query = list_purchase_prices_bound_to_product_query_factory(shop_id=dto.shop_id,
                                                                                        product_id=dto.product_id)
            data_rows = self._conn.execute(purchase_prices_query)

            if data_rows:
                data_rows = sorted(data_rows, key=lambda r: r.product_price_id)

            # make response_items
            response_items = dict()
            if not dto.group_by_supplier:
                for unit, others in groupby(data_rows, key=lambda x: x.unit):
                    response_items[unit] = [_row_to_product_price_dto(x) for x in others]
            else:
                for supplier_id, others in groupby(data_rows, key=lambda x: x.supplier_id):
                    response_items[supplier_id] = [_row_to_product_price_dto(x) for x in others]

            return list_response_factory(response_items)  # type:ignore
        except Exception as exc:
            raise exc
