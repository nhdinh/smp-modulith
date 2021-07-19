#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector

from foundation.events import EveryModuleMustCatchThisEvent
from foundation.logger import logger
from shop.application.services.shop_unit_of_work import ShopUnitOfWork


class ShopHandlerFacade:
    def __init__(self, uow: ShopUnitOfWork):
        self._uow = uow

    def do_something_with_catchall_event(self, event: EveryModuleMustCatchThisEvent):
        with self._uow as uow:  # type:ShopUnitOfWork
            try:
                uow.commit()
            except Exception as exc:
                logger.exception(exc)
                raise exc


class Shop_CatchAllEventHandler:
    @injector.inject
    def __init__(self, facade: ShopHandlerFacade):
        self._f = facade

    def __call__(self, event: EveryModuleMustCatchThisEvent):
        self._f.do_something_with_catchall_event(event)
