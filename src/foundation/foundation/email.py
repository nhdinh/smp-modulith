#!/usr/bin/env python
# -*- coding: utf-8 -*-
from abc import abstractmethod


class Email:
    @property
    @abstractmethod
    def title(self) -> str:
        pass

    @property
    @abstractmethod
    def html(self) -> str:
        pass

    @property
    @abstractmethod
    def text(self) -> str:
        pass
