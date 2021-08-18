#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

def fetch_inventory_product_balance_query_factory(warehouse_id) -> Query:
    pass


def _row_to_product_balance_dto(row):
    raise NotImplementedError


class SqlListProductsBalanceQuery(ListProductsBalanceQuery, SqlQuery):
    def query(self, dto: AuthorizedPaginationInputDto) -> PaginationOutputDto[ProductBalanceResponseDto]:
        try:
            store_id = sql_get_store_id_by_owner(store_owner=dto.current_user, conn=self._conn)
            warehouse_id = sql_get_warehouse_id_by_owner(warehouse_owner=dto.current_user, conn=self._conn)

            # get product counts
            product_counts = sql_count_products_in_store(store_id=store_id, conn=self._conn)

            # build product query
            query = fetch_inventory_product_balance_query_factory(warehouse_id=warehouse_id)
            query = query.limit(dto.page_size).offset((dto.current_page - 1) * dto.page_size)

            # query product balance
            balance_records = self._conn.execute(query).all()

            return paginate_response_factory(
                current_page=current_page,
                page_size=page_size,
                total_items=product_counts,
                items=[
                    _row_to_product_balance_dto(row) for row in balance_records
                ]
            )
        except Exception as exc:
            raise exc


def list_draft_purchase_orders_query_factory(warehouse_id: WarehouseId) -> Query:
    query = select([
        DraftPurchaseOrder,
        ShopAddress,
        ShopSupplier,
    ]) \
        .join(ShopAddress) \
        .join(ShopSupplier) \
        .join(Warehouse).where(Warehouse.warehouse_id == warehouse_id)

    return query


def list_purchase_order_items_query_factory(purchase_order_id: DraftPurchaseOrderId) -> Query:
    # query = select(DraftPurchaseOrderItem).where(DraftPurchaseOrderItem.purchase_order_id == purchase_order_id)
    query = select(draft_purchase_order_item_table).where(
        draft_purchase_order_item_table.c.purchase_order_id == purchase_order_id)

    return query


def _row_to_purchase_order_item_dto(row: RowProxy) -> PurchaseOrderItemResponseDto:
    return PurchaseOrderItemResponseDto(
        product_id=row.product_id,
        unit=row.unit_unit,
        quantity=row.quantity
    )


def _row_to_draft_purchase_order_dto(row: RowProxy, child_rows: List[RowProxy]) -> DraftPurchaseOrderResponseDto:
    return DraftPurchaseOrderResponseDto(
        purchase_order_id=row.purchase_order_id,
        supplier=_row_to_supplier_dto(row),
        delivery_address=_row_to_address_dto(row),
        creator=row.creator,
        due_date=row.due_date,
        note=row.note,
        status=row.status,
        items=[_row_to_purchase_order_item_dto(r) for r in child_rows]
    )


class SqlListDraftPurchaseOrdersQuery(ListDraftPurchaseOrdersQuery, SqlQuery):
    def query(self, dto: AuthorizedPaginationInputDto) -> PaginationOutputDto[DraftPurchaseOrderResponseDto]:
        try:
            # store_id = sql_get_store_id_by_owner(store_owner=dto.current_user, conn=self._conn)
            warehouse_id = sql_get_warehouse_id_by_owner(warehouse_owner=dto.current_user, conn=self._conn)

            # PO count
            draft_PO_count = sql_count_draft_purchase_orders_in_warehouse(warehouse_id=warehouse_id, conn=self._conn)

            # build query
            query = list_draft_purchase_orders_query_factory(warehouse_id=warehouse_id)
            query = query.limit(dto.page_size).offset((dto.current_page - 1) * dto.page_size)

            draft_purchase_orders_dtos = []
            fetched_po_rows = self._conn.execute(query).all()
            for draft_po_row in fetched_po_rows:
                draft_purchase_orders_dtos.append(_row_to_draft_purchase_order_dto(draft_po_row, child_rows=[]))

            for dpo in draft_purchase_orders_dtos:
                po_items_rows = self._conn.execute(
                    list_purchase_order_items_query_factory(purchase_order_id=dpo.purchase_order_id))
                dpo.items = [_row_to_purchase_order_item_dto(r) for r in po_items_rows]

            return paginate_response_factory(
                total_items=draft_PO_count,
                items=draft_purchase_orders_dtos,
                input_dto=dto
            )
        except Exception as exc:
            raise exc
"""
