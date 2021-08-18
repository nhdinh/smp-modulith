#!/usr/bin/env python
# -*- coding: utf-8 -*-
import uuid
from typing import Any, Optional, Tuple

import jsonpickle
import nanoid
from sqlalchemy import MetaData, String, TypeDecorator
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

metadata = MetaData()
Base = declarative_base(metadata=metadata)


def nanoid_generate(prefix: str = '', key_size: Tuple[int, int] = (20, 5)) -> str:
    if not isinstance(key_size, Tuple):
        key_size = (20, 5)
    alphabet = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return f"{prefix}_{nanoid.generate(alphabet=alphabet, size=key_size[0])}.{nanoid.generate(alphabet=alphabet, size=key_size[1])}"


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses PostgreSQL's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.

    Source: https://docs.sqlalchemy.org/en/13/core/custom_types.html#backend-agnostic-guid-type
    """

    impl = CHAR

    cache_ok = True

    def load_dialect_impl(self, dialect: Any) -> Any:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value: Any, dialect: Any) -> Optional[str]:
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value: Any, dialect: Any) -> Optional[uuid.UUID]:
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value  # type: ignore


class JsonType(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = jsonpickle.dumps(value)

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = jsonpickle.loads(value)

        return value
