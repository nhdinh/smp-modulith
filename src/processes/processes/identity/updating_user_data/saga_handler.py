#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector

from foundation import Event
from foundation.locks import LockFactory
from foundation.method_dispatch import method_dispatch
from identity.domain.events import UserDataEmitEvent
from processes.identity.updating_user_data.saga import UpdatingUserData, UpdatedUserData, State
from processes.repository import ProcessManagerDataRepo
from processes.repository import new_process_id


class UpdatingUserDataHandler:
    LOCK_TIMEOUT = 30

    @injector.inject
    def __init__(self, procman: UpdatingUserData, repo: ProcessManagerDataRepo, lock_factory: LockFactory):
        self._procman = procman
        self._repo = repo
        self._lock_factory = lock_factory

    @method_dispatch
    def __call__(self, event: Event) -> None:
        raise NotImplementedError

    @__call__.register(UserDataEmitEvent)  # type:ignore
    def handle_updating(self, event: UserDataEmitEvent) -> None:
        data = UpdatedUserData(process_id=new_process_id(), state=State.STARTED)
        lock_name = f'pm-lock-{event.user_id}-emit-data'
        self._run_process_manager(lock_name, data, event)

    def _run_process_manager(self, lock_name: str, data: UpdatedUserData, event: Event) -> None:
        lock = self._lock_factory(lock_name, self.LOCK_TIMEOUT)

        with lock:
            self._procman.handle(event, data)
            self._repo.save(data.process_id, data)
