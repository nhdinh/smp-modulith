#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import injector
from store.adapter.id_generators import generate_product_id
from store.application.services.store_unit_of_work import ShopUnitOfWork

from foundation.events import EventMixin, Event


class CollionCreatedEvent(Event):
    pass


class CollionCreatedEventHandler:
    @injector.inject
    def __init__(self, uow: ShopUnitOfWork):
        self._uow = uow

    def __call__(self, uow: ShopUnitOfWork):
        with self._uow as uow:
            try:
                c = Collision.create()
                uow.session.add(c)
                uow.commit()
            except Exception as exc:
                raise exc


class Collision(EventMixin):
    def __init__(self):
        self.id = generate_product_id()
        self.name = self.id
        self.domain_events = []

        self._record_event(CollionCreatedEvent())

    @staticmethod
    def create() -> Collision:
        c = Collision()
        return c
