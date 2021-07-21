#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import select

from db_infrastructure import SqlQuery
from foundation.events import ThingGoneInBlackHoleError
from shop.adapter.queries.query_common import sql_verify_shop_id
from shop.adapter.shop_db import shop_addresses_table, shop_table
from shop.application.queries.shop_queries import ListShopAddressesQuery, ListShopAddressesRequest
from shop.domain.dtos.shop_dtos import ShopAddressResponseDto, _row_to_address_dto
from shop.domain.entities.value_objects import ExceptionMessages
from web_app.serialization.dto import ListOutputDto


class SqlListShopAddressesQuery(ListShopAddressesQuery, SqlQuery):
    def query(self, dto: ListShopAddressesRequest) -> ListOutputDto[ShopAddressResponseDto]:
        try:
            valid_store = sql_verify_shop_id(shop_id=dto.shop_id, partner_id=dto.partner_id,
                                             conn=self._conn)
            if not valid_store:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_OWNERSHIP_NOT_FOUND)

            # query = select(StoreAddress).join(Store, StoreAddress._store).where(Store.shop_id == store_id)
            query = select(shop_addresses_table) \
                .join(shop_table, shop_addresses_table.c.shop_id == shop_table.c.shop_id).where(
                shop_table.c.shop_id == dto.shop_id)

            addresses = self._conn.execute(query).all()

            return ListOutputDto([_row_to_address_dto(row) for row in addresses])
        except Exception as exc:
            raise exc
