import abc
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Callable, Generic, List, Type, TypeVar, Optional, Union

from injector import Injector, Provider, UnsatisfiedRequirement

from db_infrastructure import nanoid_generate

T = TypeVar("T")

EVENT_ID_PREFIX = 'EVENT'
EVENT_ID_KEYSIZE = (30, 10)


def new_event_id() -> str:
    return nanoid_generate(prefix=EVENT_ID_PREFIX, key_size=EVENT_ID_KEYSIZE)


@dataclass(frozen=True)
class Event:
    event_id: str
    procman_id: Optional[str]


@dataclass(frozen=True)
class EveryModuleMustCatchThisEvent(Event):
    ...


@dataclass(frozen=True)
class WillRaiseExceptionEvent(Event):
    ...


class EventStatus(Enum):
    PENDING = 'Pending'
    FAILED = 'Failed'
    SUCCESS = 'Success'


class EventMixin:
    def __init__(self) -> None:
        self.created_at = datetime.now()
        self.last_updated = datetime.now()

        self.domain_events: List[Event] = []

    def _record_event(self, event: Union[Event, Type], **kwargs) -> None:
        """
        Add new event to `self` model.

        :param event: kind of `Event`
        """
        if not isinstance(event, Event):
            if 'procman_id' not in kwargs.keys():
                kwargs['procman_id'] = ''

            event = event(**kwargs)

        if isinstance(event, Event):
            self.domain_events.append(event)
        else:
            raise TypeError(f"{event} is not Event type")

    def clear_events(self) -> None:
        # self._pending_domain_events.clear()
        self.domain_events.clear()


class Handler(Generic[T]):
    """Simple generic used to associate handlers with events using DI.

    e.g Handler[AuctionEnded].
    """

    pass


class AsyncHandler(Generic[T]):
    """An async counterpart of Handler[Event]."""

    pass


class EventHandlerProvider(Provider):
    """Useful for configuring bind for event handlers.

    Using DI for dispatching events to handlers requires ability to bind multiple
    handlers to a single key (Handler[Event]).
    """

    def __init__(self, cls: Type[T]) -> None:
        self._cls = cls

    def get(self, injector: Injector) -> List[T]:
        return [injector.create_object(self._cls)]


class AsyncEventHandlerProvider(Provider):
    """An async counterpart of EventHandlerProvider.

    In async, one does not need to actually construct the instance.
    It is enough to obtain class itself.
    """

    def __init__(self, cls: Type[T]) -> None:
        self._cls = cls

    def get(self, _injector: Injector) -> List[Type[T]]:
        return [self._cls]


class EventBus(abc.ABC):
    @abc.abstractmethod
    def post(self, event: Event) -> None:
        raise NotImplementedError


RunAsyncHandler = Callable[[AsyncHandler[T], T], None]


class InjectorEventBus(EventBus):
    """A simple Event Bus that leverages injector.

    It requires Injector to be created with auto_bind=False.
    Otherwise UnsatisfiedRequirement is not raised. Instead,
    TypeError is thrown due to usage of `Handler` and `AsyncHandler` generics.
    """

    def __init__(self, injector: Injector, run_async_handler: RunAsyncHandler) -> None:
        self._injector = injector
        self._run_async_handler = run_async_handler

    def post(self, event: Event) -> None:
        try:
            handlers = self._injector.get(Handler[type(event)])  # type: ignore
        except UnsatisfiedRequirement as exc:
            pass
        else:
            assert isinstance(handlers, list)
            for handler in handlers:
                handler(event)

        try:
            async_handlers = self._injector.get(AsyncHandler[type(event)])  # type: ignore
        except UnsatisfiedRequirement as exc:
            pass
        else:
            assert isinstance(async_handlers, list)
            for async_handler in async_handlers:
                self._run_async_handler(async_handler, event)


class ThingGoneInBlackHoleError(Exception):
    # The 404 or Not_Found exception
    pass
