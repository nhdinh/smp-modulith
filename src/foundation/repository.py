#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from typing import Union

from sqlalchemy.orm import Session

from foundation.entity import Entity
from foundation.events import EventMixin


class AbstractRepository(abc.ABC):
    def __init__(self, session: Session):
        self._sess = session  # type:Session

    def save(self, model: Union[EventMixin, Entity]) -> None:
        self._save(model)

    @abc.abstractmethod
    def _save(self, model: Union[EventMixin, Entity]):
        raise NotImplementedError

    def delete(self, model: Union[EventMixin, Entity]) -> None:
        self.delete(model)
