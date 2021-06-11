import injector
from sqlalchemy.engine import Connection

from identity.domain.events.password_resetted_event import PasswordResettedEvent
from identity.domain.events.request_password_change_created_event import RequestPasswordChangeCreatedEvent
from store import StoreRegisteredEvent, StoreCreatedEvent
from auctions import BidderHasBeenOverbid, WinningBidPlaced
from customer_relationship.config import CustomerRelationshipConfig
from customer_relationship.facade import CustomerRelationshipFacade
from customer_relationship.models import customers
from foundation.events import AsyncEventHandlerProvider, AsyncHandler

__all__ = [
    # module
    "CustomerRelationship",
    "CustomerRelationshipConfig",
    # facade
    "CustomerRelationshipFacade",
    # models
    "customers",
]


class CustomerRelationship(injector.Module):
    @injector.provider
    def facade(self, config: CustomerRelationshipConfig, connection: Connection) -> CustomerRelationshipFacade:
        return CustomerRelationshipFacade(config, connection)

    def configure(self, binder: injector.Binder) -> None:
        binder.multibind(AsyncHandler[BidderHasBeenOverbid], to=AsyncEventHandlerProvider(BidderHasBeenOverbidHandler))
        binder.multibind(AsyncHandler[WinningBidPlaced], to=AsyncEventHandlerProvider(WinningBidPlacedHandler))
        binder.multibind(AsyncHandler[StoreRegisteredEvent], to=AsyncEventHandlerProvider(StoreRegisteredEventHandler))
        binder.multibind(AsyncHandler[StoreCreatedEvent],
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

    def __call__(self, event: StoreRegisteredEvent) -> None:
        self._facade.send_store_registration_confirmation_token_email(
            event.store_name, event.confirmation_token,
            event.owner_email
        )


class StoreCreatedSuccessfullyEventHandler:
    @injector.inject
    def __init__(self, facade: CustomerRelationshipFacade) -> None:
        self._facade = facade

    def __call__(self, event: StoreCreatedEvent) -> None:
        self._facade.send_store_created_email(
            store_name=event.store_name,
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
