#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import injector
from store.application.services.store_unit_of_work import StoreUnitOfWork

from foundation.events import EventMixin, Event
from store.adapter.id_generators import generate_product_id


class CollionCreatedEvent(Event):
    pass


class CollionCreatedEventHandler:
    @injector.inject
    def __init__(self, uow: StoreUnitOfWork):
        self._uow = uow

    def __call__(self, uow: StoreUnitOfWork):
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
