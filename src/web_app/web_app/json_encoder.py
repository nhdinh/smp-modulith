from datetime import datetime
from functools import singledispatchmethod
import json

from foundation.value_objects import Money

from auctions import AuctionDto
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
            'id': str(obj.id),
            'reference': obj.reference,
            'display_name': obj.display_name,
            'disabled': obj.disabled,
        }

    @default.register(Money)  # noqa: F811
    def serialize_money(self, obj: Money) -> object:
        return {"amount": str(obj.amount), "currency": obj.currency.iso_code}

    @default.register(datetime)  # noqa: F811
    def serialize_datetime(self, obj: datetime) -> str:
        return obj.isoformat()
