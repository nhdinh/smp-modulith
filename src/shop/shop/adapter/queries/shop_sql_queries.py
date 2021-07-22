#!/usr/bin/env python
# -*- coding: utf-8 -*-
from foundation.database_setup import location_address_table
from sqlalchemy import select

from db_infrastructure import SqlQuery
from foundation.events import ThingGoneInBlackHoleError
from shop.adapter.queries.query_common import sql_verify_shop_id
from shop.adapter.shop_db import shop_addresses_table, shop_table, shop_users_table
from shop.application.queries.shop_queries import ListShopAddressesQuery, ListShopAddressesRequest, GetShopInfoRequest, \
    GetShopInfoQuery
from shop.domain.dtos.shop_dtos import ShopAddressResponseDto, _row_to_address_dto, ShopInfoResponseDto, \
    _row_to_shop_info_dto
from shop.domain.entities.value_objects import ExceptionMessages
from web_app.serialization.dto import ListOutputDto


class SqlListShopAddressesQuery(ListShopAddressesQuery, SqlQuery):
    def query(self, dto: ListShopAddressesRequest) -> ListOutputDto[ShopAddressResponseDto]:
        try:
            valid_store = sql_verify_shop_id(shop_id=dto.shop_id, partner_id=dto.partner_id,
                                             conn=self._conn)
            if not valid_store:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_OWNERSHIP_NOT_FOUND)

            query = select([
                shop_addresses_table,
                location_address_table,
            ]) \
                .join(location_address_table, location_address_table.c.address_id == shop_addresses_table.c.address_id) \
                .where(shop_table.c.shop_id == dto.shop_id)

            addresses = self._conn.execute(query).all()

            return ListOutputDto([_row_to_address_dto(row) for row in addresses])
        except Exception as exc:
            raise exc


class SqlGetShopInfoQuery(GetShopInfoQuery, SqlQuery):
    def query(self, dto: GetShopInfoRequest) -> ListOutputDto[ShopInfoResponseDto]:
        try:
            query = select([shop_table]) \
                .join(shop_users_table, shop_users_table.c.shop_id == shop_table.c.shop_id).where(
                shop_users_table.c.user_id == dto.partner_id)

            shops = self._conn.execute(query).all()

            return ListOutputDto([_row_to_shop_info_dto(row) for row in shops])
        except Exception as exc:
            raise exc
