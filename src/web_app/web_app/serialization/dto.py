import decimal
from typing import Type, TypeVar, cast, List

from flask import Request
from marshmallow import Schema, exceptions, EXCLUDE, INCLUDE
from marshmallow.fields import Decimal
from marshmallow_dataclass import class_schema, dataclass

from foundation.value_objects import Money
from web_app.serialization.fields import Dollars

TDto = TypeVar("TDto")


class BaseSchema(Schema):
    TYPE_MAPPING = {
        Money: Dollars,
    }


@dataclass
class PaginationInputDto:
    page: int
    page_size: int


@dataclass
class PaginationOutputDto:
    items: List
    current_page: int
    page_size: int
    total_items: int
    total_pages: int


def get_dto(request: Request, dto_cls: Type[TDto], context: dict) -> TDto:
    schema_cls = class_schema(dto_cls, base_schema=BaseSchema)
    schema = schema_cls()
    try:
        request_json = getattr(request, 'json', {})
        request_json = request_json if request_json else {}

        return cast(TDto, schema.load(dict(context, **request_json), unknown=EXCLUDE))
    except exceptions.ValidationError as exc:
        raise exc
