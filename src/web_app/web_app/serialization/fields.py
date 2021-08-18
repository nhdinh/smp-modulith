import typing
import uuid
from uuid import UUID

from marshmallow import exceptions, fields

from foundation.value_objects.factories import get_money


class Dollars(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):  # type: ignore
        return str(value)

    def _deserialize(self, value, attr, data, **kwargs):  # type: ignore
        try:
            return get_money(value)
        except ValueError as exc:
            raise exceptions.ValidationError(str(exc))


class Guid(fields.Field):
    def _serialize(self, value: UUID, attr: str, obj: UUID, **kwargs):
        return str(value)

    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Optional[str],
            data: typing.Optional[typing.Mapping[str, typing.Any]],
            **kwargs
    ):
        try:
            return uuid.UUID(value)
        except ValueError as exc:
            raise exceptions.ValidationError(str(exc))
