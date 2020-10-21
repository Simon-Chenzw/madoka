from __future__ import absolute_import

import asyncio
import logging
from typing import TYPE_CHECKING, Callable, Dict, List, Union

import websockets

from .base import BotBase
from .data import Context, Event

if TYPE_CHECKING:
    from .bot import QQbot

logger = logging.getLogger(__name__)


class MessageUnit(BotBase):
    def __init__(self, *args, **kwargs) -> None:
        self._function: List[Callable[['QQbot', Context], None]] = []
        super().__init__(*args, **kwargs)

    def addFunction(
        self,
        func: Callable[['QQbot', Context], None],
    ) -> None:
        logger.debug(f"add function: {func.__name__ }")
        self._function.append(func)

    async def _messageReceiver(self) -> None:
        logger.info("listening message")
        async with websockets.connect(
                f"ws://{self.socket}/message?sessionKey={self.session}"
        ) as websocket:
            async for message in websocket:
                asyncio.create_task(self._messageSolve(message))

    async def _messageSolve(self, message: Union[str, bytes]) -> None:
        if isinstance(message, bytes):
            logger.error(f"get byte message {message}")
            return
        # TODO: low performance. should use 'run_in_executor'
        logger.debug(f"get message: {message}")
        for func in self._function:
            try:
                func(self._bot, Context(message))
            except Exception as err:
                logger.exception(f"message solve: {func.__name__}\n {message}")


class EventUnit(BotBase):
    def __init__(self, *args, **kwargs) -> None:
        self._event: Dict[str, List[Callable[['QQbot', Event], None]]] = {}
        super().__init__(*args, **kwargs)

    def addEvent(
        self,
        eventType: str,
        func: Callable[['QQbot', Event], None],
    ) -> None:
        logger.debug(f"add event: {func.__name__ }")
        self._event.setdefault(eventType, [])
        self._event[eventType].append(func)

    async def _eventReceiver(self) -> None:
        logger.info("listening event")
        async with websockets.connect(
                f"ws://{self.socket}/event?sessionKey={self.session}"
        ) as websocket:
            async for message in websocket:
                asyncio.create_task(self._eventSolve(message))

    async def _eventSolve(self, message: Union[str, bytes]) -> None:
        if isinstance(message, bytes):
            logger.error(f"get byte message {message}")
            return
        # TODO: low performance. should use 'run_in_executor'
        logger.debug(f"get event: {message}")
        try:
            event = Event(message)
        except Exception as err:
            logger.info(f"wrong event format: {message}")
            return
        for func in self._event.get(event.type, []) + self._event.get(
                'any', []):
            try:
                func(self._bot, event)
            except Exception as err:
                logger.exception(f"event solve: {func.__name__}\n {message}")


class ReceiveUnit(MessageUnit, EventUnit):
    async def _receiver(self) -> None:
        await asyncio.gather(
            self._messageReceiver(),
            self._eventReceiver(),
        )
