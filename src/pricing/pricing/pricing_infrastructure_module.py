#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector
from foundation import EventBus
from sqlalchemy.engine import Connection
from sqlalchemy.orm import sessionmaker

from pricing.services.pricing_uow import PricingUnitOfWork


class PricingInfrastructureModule(injector.Module):
    @injector.provider
    def uow(self, conn: Connection, event_bus: EventBus) -> PricingUnitOfWork:
        sessfactory = sessionmaker(bind=conn)
        return PricingUnitOfWork(sessionfactory=sessfactory, event_bus=event_bus)

    # @injector.provider
    # def list_shop_product_purchase_prices_query(self, conn: Connection) -> ListShopProductPurchasePricesQuery:
    #     return SqlListShopProductPurchasePricesQuery(conn)
    #
    # @injector.provider
    # def get_shop_product_purchase_price(self, conn: Connection) -> GetShopProductPurchasePriceQuery:
    #     return SqlGetShopProductPurchasePriceQuery(conn)
    #
    # @injector.provider
    # def get_shop_product_lowest_purchase_price(self, conn: Connection) -> GetShopProductLowestPurchasePriceQuery:
    #     return SqlGetShopProductLowestPurchasePriceQuery(conn)
