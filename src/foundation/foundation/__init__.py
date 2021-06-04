#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector

from foundation.email import Email
from foundation.events import AsyncHandler, AsyncEventHandlerProvider
from foundation.helpers.email_sender import DefaultEmailConfig, EmailSender
from product_catalog.domain.events.store_registered_event import StoreRegisteredEvent


class FoundationModuleFacade:
    def __init__(self, config: DefaultEmailConfig) -> None:
        self._sender = EmailSender(config=config)

    def _send(self, recipient: str, email: Email) -> None:
        self._sender.send(recipient, email)


class FoundationModule(injector.Module):
    @injector.provider
    def facade(self, config: DefaultEmailConfig) -> FoundationModuleFacade:
        return FoundationModuleFacade(config=config)

    def configure(self, binder: injector.Binder) -> None:
        binder.multibind(AsyncHandler[StoreRegisteredEvent], to=AsyncEventHandlerProvider(StoreRegisteredEventHandler))


class StoreRegisteredEventHandler:
    @injector.inject
    def __init__(self, facade: FoundationModuleFacade):
        self._f = facade

    def __call__(self, event: StoreRegisteredEvent) -> None:
        print('StoreRegisteredEventHandler do something')
