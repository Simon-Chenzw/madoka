from __future__ import annotations

import asyncio
import logging
from contextvars import ContextVar
from typing import TYPE_CHECKING, Dict, List, Union

import websockets

from ..typing import Context, Event
from .base import BotBase

if TYPE_CHECKING:
    from ..typing.frame import contextFunc, eventFunc

logger = logging.getLogger('madoka')

contextStore: ContextVar[Context] = ContextVar('context')


class MessageUnit(BotBase):
    _function: List[contextFunc] = []

    def addFunction(self, func: contextFunc) -> None:
        logger.debug(f"add function: {func.__name__ }")
        self._function.append(func)

    async def _messageReceiver(self) -> None:
        logger.info("listening message")
        async with websockets.connect(
                f"ws://{self._socket}/message?sessionKey={self._session}"
        ) as websocket:
            async for message in websocket:
                # TODO use Queue to track future
                self.create_task(self._messageSolve(message))

    async def _messageSolve(self, message: Union[bytes, str]) -> None:
        async def solve(func: contextFunc) -> None:
            try:
                ret = func(self._bot, context)
                if ret and asyncio.iscoroutine(ret):
                    await ret
            except:
                logger.exception(f"message solve: {func.__name__}\n {message}")

        if isinstance(message, str):
            logger.debug(f"get message: {message}")
            context = Context(message)
            contextStore.set(context)
            await asyncio.gather(*map(solve, self._function))
        else:
            logger.error(f"get bytes message, {message=}")


class EventUnit(BotBase):
    _event: Dict[str, List[eventFunc]] = {}

    def addEvent(self, eventType: str, func: eventFunc) -> None:
        logger.debug(f"add event: {eventType} {func.__name__ }")
        self._event.setdefault(eventType, []).append(func)

    async def _eventReceiver(self) -> None:
        logger.info("listening event")
        async with websockets.connect(
                f"ws://{self._socket}/event?sessionKey={self._session}"
        ) as websocket:
            async for message in websocket:
                self.create_task(self._eventSolve(message))

    async def _eventSolve(self, message: Union[str, bytes]) -> None:
        async def solve(func: eventFunc) -> None:
            try:
                ret = func(self._bot, event)
                if ret and asyncio.iscoroutine(ret):
                    await ret
            except:
                logger.exception(f"event solve: {func.__name__}\n {message}")

        if isinstance(message, str):
            logger.debug(f"get event: {message}")
            event = Event(message)
            await asyncio.gather(*map(
                solve,
                self._event.get(event.type, []) + self._event.get('any', []),
            ))
        else:
            logger.error(f"get byte message {message}")


class ReceiveUnit(MessageUnit, EventUnit):
    async def _receiver(self) -> None:
        await asyncio.gather(
            self._messageReceiver(),
            self._eventReceiver(),
        )
