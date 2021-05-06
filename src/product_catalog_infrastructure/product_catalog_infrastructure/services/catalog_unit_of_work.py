#!/usr/bin/env python
# -*- coding: utf-8 -*-
from foundation.uow import SqlAlchemyUnitOfWork


class CatalogUnitOfWork(SqlAlchemyUnitOfWork):
    def __init__(self):
        super(CatalogUnitOfWork, self).__init__()


    def _collect_new_events(self):
        pass
