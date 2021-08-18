from typing import Callable, Dict, List, Tuple, Type

import injector
from sqlalchemy.engine import Connection
from typing_extensions import Protocol

from customer_relationship import CustomerRelationshipFacade
from foundation.events import AsyncEventHandlerProvider, AsyncHandler, Event
from identity import IdentityHandlerFacade
from inventory import InventoryHandlerFacade
from payments import PaymentsFacade
from processes.identity.updating_user_data import UpdatingUserData, UpdatingUserDataHandler
from processes.paying_for_won_item import PayingForWonItem, PayingForWonItemHandler
from processes.repository import ProcessManagerDataRepo
from processes.shop.modifying_shop_product import ShopCreatingNewProductHandler, ShopCreatingNewProduct
from processes.shop.registering_new_shop import RegisteringNewShop, RegisteringNewShopHandler
from shop import ShopHandlerFacade

__all__ = [
    # module
    "Processes"
]


class Handler(Protocol):
    registry: Dict[Type, Callable]

    def __call__(self, event: Event) -> None:
        ...


class ProcessManager(Protocol):
    handle: Handler


class Processes(injector.Module):
    PM_HANDLERS: List[Tuple[Type[ProcessManager], Type[Handler]]] = [
        (PayingForWonItem, PayingForWonItemHandler),
        (ShopCreatingNewProduct, ShopCreatingNewProductHandler),
        (RegisteringNewShop, RegisteringNewShopHandler),
        (UpdatingUserData, UpdatingUserDataHandler)
    ]

    @injector.provider
    def get_paying_for_won_item(
            self, payments: PaymentsFacade, customer_relationship: CustomerRelationshipFacade
    ) -> PayingForWonItem:
        return PayingForWonItem(payments, customer_relationship)

    @injector.provider
    def creating_new_shop_product(self, shop_facade: ShopHandlerFacade,
                                  inventory_facade: InventoryHandlerFacade) -> ShopCreatingNewProduct:
        return ShopCreatingNewProduct(shop_facade=shop_facade, inventory_facade=inventory_facade)

    @injector.provider
    def registering_new_shop(self, identity_facade: IdentityHandlerFacade,
                             shop_facade: ShopHandlerFacade,
                             inventory_facade: InventoryHandlerFacade,
                             crm_facade: CustomerRelationshipFacade) -> RegisteringNewShop:
        return RegisteringNewShop(identity_facade=identity_facade,
                                  shop_facade=shop_facade,
                                  inventory_facade=inventory_facade,
                                  crm_facade=crm_facade)

    @injector.provider
    def updating_user_data(self, shop_facade: ShopHandlerFacade,
                           inventory_facade: InventoryHandlerFacade) -> UpdatingUserData:
        return UpdatingUserData(shop_facade=shop_facade, inventory_facade=inventory_facade)

    @injector.provider
    def get_data_repo(self, connection: Connection) -> ProcessManagerDataRepo:
        return ProcessManagerDataRepo(connection)

    def configure(self, binder: injector.Binder) -> None:
        for pm, handler_cls in self.PM_HANDLERS:
            handled_events = [event for event in pm.handle.registry.keys() if issubclass(event, Event)]
            for event in handled_events:
                binder.multibind(AsyncHandler[event], to=AsyncEventHandlerProvider(handler_cls))

        return None
