#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import uuid
from datetime import datetime

from typing import List, Optional

from foundation.events import EventMixin
from product_catalog.domain.entities.collection import Collection
from product_catalog.domain.events import CollectionCreatedEvent
from product_catalog.domain.value_objects import CatalogId, CatalogReference, CollectionReference


class Catalog(EventMixin):
    def __init__(
            self,
            id: CatalogId,
            reference: CatalogReference,
            display_name: str
    ):
        super(Catalog, self).__init__()

        # TODO: check rule(s) on:
        # collection_reference (not_null; well_formed);
        # display_name (not_null)

        self.id = id
        self.reference = reference
        self.display_name = display_name

        self._collections: List[Collection] = []
        self._default_collection: Optional[Collection] = None

        self._created_at = datetime.now()

    def create_child_collection(
            self,
            collection_reference: CollectionReference,
            display_name: str
    ) -> None:
        # TODO: check rule(s) on:
        # collection_reference (not_null; well_formed);
        # display_name (not_null)

        self._collections.append(
            Collection(
                reference=collection_reference,
                display_name=display_name
            )
        )

        self._record_event(CollectionCreatedEvent(
            reference=collection_reference,
            catalog_id=self.id,
            catalog_reference=self.reference
        ))

    def __str__(self) -> str:
        return f'<Catalog #{self.id} reference="{self.reference}" display_name="{self.display_name}">'

    def __eq__(self, other: Catalog) -> bool:
        return isinstance(other, Catalog) and vars(self) == vars(other)

    @staticmethod
    def create(reference, display_name, **kwargs):
        catalog = Catalog(
            id=uuid.uuid4(),
            reference=reference,
            display_name=display_name
        )

        return catalog
