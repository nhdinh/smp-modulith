import injector
from auctions import BidderHasBeenOverbid, WinningBidPlaced
from sqlalchemy.engine import Connection

from customer_relationship.config import CustomerRelationshipConfig
from customer_relationship.facade import CustomerRelationshipFacade
from customer_relationship.models import customers
from foundation.domain_events.shop_events import ShopCreatedEvent, ShopRegisteredEvent, ShopRegistrationResendEvent
from foundation.events import AsyncEventHandlerProvider, AsyncHandler, EveryModuleMustCatchThisEvent
from foundation.logger import logger
from identity.domain.events.password_resetted_event import PasswordResettedEvent
from identity.domain.events.request_password_change_created_event import RequestPasswordChangeCreatedEvent

__all__ = [
    # module
    "CustomerRelationshipEventHandlerModule",
    "CustomerRelationshipConfig",
    # facade
    "CustomerRelationshipFacade",
    # models
    "customers",
]


class CustomerRelationshipEventHandlerModule(injector.Module):
    @injector.provider
    def facade(self, config: CustomerRelationshipConfig, connection: Connection) -> CustomerRelationshipFacade:
        return CustomerRelationshipFacade(config, connection)

    def configure(self, binder: injector.Binder) -> None:
        binder.multibind(AsyncHandler[EveryModuleMustCatchThisEvent],
                         to=AsyncEventHandlerProvider(CRM_CatchAllEventHandler))
        binder.multibind(AsyncHandler[BidderHasBeenOverbid], to=AsyncEventHandlerProvider(BidderHasBeenOverbidHandler))
        binder.multibind(AsyncHandler[WinningBidPlaced], to=AsyncEventHandlerProvider(WinningBidPlacedHandler))
        binder.multibind(AsyncHandler[ShopRegisteredEvent], to=AsyncEventHandlerProvider(StoreRegisteredEventHandler))
        binder.multibind(AsyncHandler[ShopRegistrationResendEvent],
                         to=AsyncEventHandlerProvider(StoreRegistrationResendEventHandler))
        binder.multibind(AsyncHandler[ShopCreatedEvent],
                         to=AsyncEventHandlerProvider(StoreCreatedSuccessfullyEventHandler))
        binder.multibind(AsyncHandler[RequestPasswordChangeCreatedEvent],
                         to=AsyncEventHandlerProvider(RequestPasswordChangeCreatedEventHandler))
        binder.multibind(AsyncHandler[PasswordResettedEvent],
                         to=AsyncEventHandlerProvider(PasswordResettedEventHandler))


class BidderHasBeenOverbidHandler:
    @injector.inject
    def __init__(self, facade: CustomerRelationshipFacade) -> None:
        self._facade = facade

    def __call__(self, event: BidderHasBeenOverbid) -> None:
        self._facade.send_email_about_overbid(event.bidder_id, event.new_price, event.auction_title)


class WinningBidPlacedHandler:
    @injector.inject
    def __init__(self, facade: CustomerRelationshipFacade) -> None:
        self._facade = facade

    def __call__(self, event: WinningBidPlaced) -> None:
        self._facade.send_email_about_winning(event.bidder_id, event.bid_amount, event.auction_title)


class StoreRegisteredEventHandler:
    @injector.inject
    def __init__(self, facade: CustomerRelationshipFacade) -> None:
        self._facade = facade

    def __call__(self, event: ShopRegisteredEvent) -> None:
        self._facade.send_store_registration_confirmation_token_email(
            event.shop_name, event.confirmation_token,
            event.owner_email
        )


class StoreRegistrationResendEventHandler:
    @injector.inject
    def __init__(self, facade: CustomerRelationshipFacade) -> None:
        self._facade = facade

    def __call__(self, event: ShopRegistrationResendEvent) -> None:
        self._facade.send_store_registration_confirmation_token_email(
            event.shop_name, event.confirmation_token,
            event.owner_email
        )


class StoreCreatedSuccessfullyEventHandler:
    @injector.inject
    def __init__(self, facade: CustomerRelationshipFacade) -> None:
        self._facade = facade

    def __call__(self, event: ShopCreatedEvent) -> None:
        self._facade.send_store_created_email(
            store_name=event.shop_name,
            owner_name=event.owner_name,
            owner_email=event.owner_email
        )


class RequestPasswordChangeCreatedEventHandler:
    @injector.inject
    def __init__(self, facade: CustomerRelationshipFacade) -> None:
        self._facade = facade

    def __call__(self, event: RequestPasswordChangeCreatedEvent) -> None:
        self._facade.send_password_reset_token_email(
            username=event.username,
            user_email=event.email,
            token=event.token
        )


class PasswordResettedEventHandler:
    @injector.inject
    def __init__(self, facade: CustomerRelationshipFacade) -> None:
        self._facade = facade

    def __call__(self, event: PasswordResettedEvent) -> None:
        self._facade.send_password_reset_notification(
            username=event.username,
            user_email=event.email
        )


class CRM_CatchAllEventHandler:
    @injector.inject
    def __init__(self):
        ...

    def __call__(self, event: EveryModuleMustCatchThisEvent):
        logger.debug(f'Identity_{event.event_id}')
