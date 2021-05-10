#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import abc


class BusinessRuleValidationError(Exception):
    def __init__(self, broken_rule: BusinessRuleBase):
        super(BusinessRuleValidationError, self).__init__()
        self._broken_rule = broken_rule
        self._details = self._broken_rule.message

    @property
    def details(self):
        return self._details

    def __repr__(self):
        return f"{self._broken_rule.__class__}: {self._broken_rule.message}"


class BusinessRuleBase(abc.ABC):
    def __init__(self, message: str = None):
        if message is None:
            raise Exception("Rule must have self-explaination message.")
        self._message = message

    @abc.abstractmethod
    def is_broken(self) -> bool:
        raise NotImplementedError

    @property
    def message(self):
        return self._message
