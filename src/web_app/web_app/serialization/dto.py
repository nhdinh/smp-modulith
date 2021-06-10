from dataclasses import field
from typing import Type, TypeVar, cast, List
import marshmallow as ma

from flask import Request
from marshmallow_dataclass import class_schema, dataclass

from foundation.value_objects import Money
from web_app.serialization.fields import Dollars

TDto = TypeVar("TDto")


class BaseSchema(ma.Schema):
    TYPE_MAPPING = {
        Money: Dollars,
    }


@dataclass
class PaginationInputDto:
    page: int
    page_size: int


@dataclass
class PaginationOutputDto:
    current_page: int
    page_size: int
    total_items: int
    total_pages: int
    # items: List = field(default_factory=list)

    def serialize(self):
        return {
            'current_page': self.current_page,
            'page_size': self.page_size,
            'total_pages': self.total_pages,
            'total_items': self.total_items,
            # 'items': self.items
        }


def get_dto(request: Request, dto_cls: Type[TDto], context: dict) -> TDto:
    schema_cls = class_schema(dto_cls, base_schema=BaseSchema)
    schema = schema_cls()
    try:
        request_json = getattr(request, 'json', {})
        request_json = request_json if request_json else {}

        return cast(TDto, schema.load(dict(context, **request_json), unknown=ma.EXCLUDE))
    except ma.exceptions.ValidationError as exc:
        raise exc
