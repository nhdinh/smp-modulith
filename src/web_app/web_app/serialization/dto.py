import math
from dataclasses import field
from typing import Type, TypeVar, cast, List, Generic
import marshmallow as ma

from flask import Request
from marshmallow_dataclass import class_schema, dataclass

from foundation.value_objects import Money
from web_app.serialization.fields import Dollars

T = TypeVar("T")
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
class AuthorizedPaginationInputDto:
    current_user: str
    page: int = 1
    page_size: int = 10


@dataclass(frozen=True)
class PaginationOutputDto(Generic[T]):
    current_page: int
    page_size: int
    total_items: int
    total_pages: int
    # items: List[T] = field(default_factory=list)

    # thanks for the fix at https://github.com/lovasoa/marshmallow_dataclass/issues/141
    items: List[T] = field(metadata={"marshmallow_field": ma.fields.Raw()}, default_factory=list)

    def serialize(self):
        return {
            'current_page': self.current_page,
            'page_size': self.page_size,
            'total_pages': self.total_pages,
            'total_items': self.total_items,
            'items': self.items
        }


def paginate_response_factory(
        items: List[T],
        current_page: int,
        page_size: int,
        total_items: int
) -> PaginationOutputDto[T]:
    """
    Create a paginate response data object from input params

    :param items: List of Data Object as the core of response object
    :param current_page: current page number
    :param page_size: size of items in a single page
    :param total_items: total of items can be fetched
    :return:
    """
    return PaginationOutputDto(
        current_page,
        page_size,
        total_items,
        math.ceil(total_items / page_size),
        items
    )


def get_dto(request: Request, dto_cls: Type[TDto], context: dict) -> TDto:
    schema_cls = class_schema(dto_cls, base_schema=BaseSchema)
    schema = schema_cls()
    input_data ={}
    try:
        request_json = getattr(request, 'json', {})
        request_json = request_json if request_json else {}

        request_form = getattr(request, 'form', {})
        request_form = request_form if request_form else {}

        # collect all data
        input_data.update(request_json)
        input_data.update(request_form)

        # parse them
        return cast(TDto, schema.load(dict(context, **input_data), unknown=ma.EXCLUDE))
    except ma.exceptions.ValidationError as exc:
        raise exc
