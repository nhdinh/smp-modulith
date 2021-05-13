import json
from datetime import datetime
from functools import singledispatchmethod
from uuid import UUID

from auctions import AuctionDto
from auth.application.queries.identity import UserDto
from foundation.value_objects import Money
from product_catalog.application.queries.product_catalog import CatalogDto


class JSONEncoder(json.JSONEncoder):
    @singledispatchmethod
    def default(self, obj: object) -> object:
        raise TypeError(f"Cannot serialize {type(obj)}")

    @default.register(AuctionDto)  # noqa: F811
    def serialize_auction_dto(self, obj: AuctionDto) -> object:
        return {
            "id": obj.id,
            "title": obj.title,
            "current_price": obj.current_price,
            "starting_price": obj.starting_price,
            "ends_at": obj.ends_at,
        }

    @default.register(CatalogDto)  # noqa: F811
    def serialize_catalog_dto(self, obj: CatalogDto) -> object:
        return {
            'reference': obj.reference,
            'display_name': obj.display_name,
            'disabled': obj.disabled,
        }

    @default.register(UserDto)  # noqa: F811
    def serialize_user_dto(self, obj: UserDto) -> object:
        return {
            'id': obj.id,
            'email': obj.email
        }

    @default.register(Money)  # noqa: F811
    def serialize_money(self, obj: Money) -> object:
        return {"amount": str(obj.amount), "currency": obj.currency.iso_code}

    @default.register(datetime)  # noqa: F811
    def serialize_datetime(self, obj: datetime) -> str:
        return obj.isoformat()

    @default.register(UUID)  # noqa: F811
    def serialize_uuid(self, obj: UUID) -> str:
        return str(obj)
