#!/usr/bin/env python
# -*- coding: utf-8 -*-
from foundation.events import EventMixin
from inventory.domain.entities.product import InventoryProductId


class Inventory(EventMixin):
    def __init__(self):
        super(Inventory, self).__init__()

    def get_product_available_stock(self, product_id: InventoryProductId):
        return ('default_unit', 'unit_1', 'unit_2'), (10, 20, 30)

    def new_draft_stocking_batch(self) -> 'StockBatch':
        batch = StockBatch.new_draft()
        batch.is_draft = True
        return batch

    def update_draft_stocking_batch(self, batch_id):
        # get batch, if batch is draft then ok
        # upate, add remove or do so so
        return batch

    def commit_stocking_batch(self):
        batch.is_draft = False
        batch.commit()

        return batch

    def generate_draft_stocking_batch(self) -> 'StockBatch':
        # get all product that need restock
        # generate batch
        return batch

    def create_return_from_batch(self, batch_id, items: List[BatchItem]):
        # get batch item from batch
        # generate a return
        return batch
