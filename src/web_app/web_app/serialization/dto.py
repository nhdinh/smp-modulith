import math
from dataclasses import field
from typing import Type, TypeVar, cast, List, Generic, Union, Optional

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
class BaseInputDto:
    timestamp: int


@dataclass
class BaseShopInputDto(BaseInputDto):
    partner_id: 'SystemUserId'
    shop_id: 'ShopId'


@dataclass
class PaginationInputDto:
    page: Optional[int] = 1
    page_size: Optional[int] = 10
    current_page: int = 1


@dataclass
class AuthorizedPaginationInputDto(PaginationInputDto, BaseShopInputDto):
    ...


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
        total_items: int,
        input_dto: Union[PaginationInputDto, AuthorizedPaginationInputDto],
) -> PaginationOutputDto[T]:
    """
    Create a paginate response data object from input params

    :param input_dto:
    :param items: List of Data Object as the core of response object
    :param total_items: total of items can be fetched
    :return:
    """
    return PaginationOutputDto(
        input_dto.current_page,
        input_dto.page_size,
        total_items,
        math.ceil(total_items / input_dto.page_size),
        items
    )


def get_dto(request: Request, dto_cls: Type[TDto], context: dict) -> TDto:
    schema_cls = class_schema(dto_cls, base_schema=BaseSchema)
    schema = schema_cls()
    input_data = {}
    try:
        request_json = getattr(request, 'json', {})
        request_json = request_json if request_json else {}

        request_form = getattr(request, 'form', {})
        request_form = request_form if request_form else {}

        # collect all data
        input_data.update(request_json)
        input_data.update(request_form)

        # parse them
        dto = cast(TDto, schema.load(dict(input_data, **context), unknown=ma.EXCLUDE))

        # clean input of pagination
        if isinstance(dto, AuthorizedPaginationInputDto) or isinstance(dto, PaginationInputDto):
            try:
                dto.page = int(dto.page) if int(dto.page) > 0 else 1
                dto.page_size = int(dto.page_size) if int(dto.page_size) > 0 else 10
            except:
                dto.page = 1
                dto.page_size = 10

        return dto
    except ma.exceptions.ValidationError as exc:
        raise exc
