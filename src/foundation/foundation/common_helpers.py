#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional
from uuid import UUID

import slugify as slug1fy

AWS_ALLOWED_SEPARATOR = '-'

def slugify(text: str) -> str:
    if text is None:
        return text

    return slug1fy.slugify(text.strip(), separator=AWS_ALLOWED_SEPARATOR)


def short_id(text: str) -> str:
    return text[-6:]


def uuid_validate(text: str) -> Optional[UUID]:
    """
    Try to validate a string as an UUID

    :param text: input string
    :return: an UUID if valid, else None
    """
    try:
        return UUID(text)
    except:
        return None
