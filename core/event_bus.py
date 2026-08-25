"""
Thread-safe event bus supporting synchronous callbacks and async subscribers.
"""
import inspect
import asyncio
from typing import Callable, Dict, List, Type, Any, Optional
from collections import defaultdict
from utils.logger import get_logger
from .events import Event

logger = get_logger("event_bus")


class EventBus:
    """Thread-safe publish/subscribe bus for inter-component communication."""

    def __init__(self):
        self._subscribers: Dict[Type[Event], List[Callable[[Any], None]]] = defaultdict(list)
        self._async_subscribers: Dict[Type[Event], List[Callable[[Any], Any]]] = defaultdict(list)
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def set_event_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop

    def subscribe(self, event_type: Type[Event], handler: Callable[[Any], None]) -> None:
        """Subscribe a handler (sync or async) to a specific event type."""
        if inspect.iscoroutinefunction(handler):
            if handler not in self._async_subscribers[event_type]:
                self._async_subscribers[event_type].append(handler)
        else:
            if handler not in self._subscribers[event_type]:
                self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: Type[Event], handler: Callable[[Any], None]) -> None:
        if handler in self._subscribers.get(event_type, []):
            self._subscribers[event_type].remove(handler)
        if handler in self._async_subscribers.get(event_type, []):
            self._async_subscribers[event_type].remove(handler)

    def publish(self, event: Event) -> None:
        """Publish an event to all subscribers."""
        event_type = type(event)

        # 1. Notify sync subscribers
        for handler in self._subscribers.get(event_type, []):
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Error in sync event handler for {event_type.__name__}: {e}", exc_info=True)

        # 2. Notify async subscribers
        async_handlers = self._async_subscribers.get(event_type, [])
        if async_handlers:
            if self._loop and self._loop.is_running():
                for a_handler in async_handlers:
                    asyncio.run_coroutine_threadsafe(self._safe_async_call(a_handler, event), self._loop)
            else:
                try:
                    # Attempt current running loop
                    curr_loop = asyncio.get_running_loop()
                    for a_handler in async_handlers:
                        curr_loop.create_task(self._safe_async_call(a_handler, event))
                except RuntimeError:
                    # No active event loop in thread; schedule if loop available
                    pass

    async def _safe_async_call(self, handler: Callable[[Any], Any], event: Event) -> None:
        try:
            await handler(event)
        except Exception as e:
            logger.error(f"Error in async event handler for {type(event).__name__}: {e}", exc_info=True)

    def clear(self) -> None:
        self._subscribers.clear()
        self._async_subscribers.clear()


_GLOBAL_EVENT_BUS: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    global _GLOBAL_EVENT_BUS
    if _GLOBAL_EVENT_BUS is None:
        _GLOBAL_EVENT_BUS = EventBus()
    return _GLOBAL_EVENT_BUS
