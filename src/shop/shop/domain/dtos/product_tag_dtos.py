#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from sqlalchemy.engine.row import RowProxy


def _row_to_tag_dto(row: RowProxy):
  return row.tag


@dataclass
class StoreProductTagDto:
  tag: str

  def serialize(self):
    return {
      'tag': self.tag
    }
