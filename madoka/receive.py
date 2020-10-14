from __future__ import absolute_import

import asyncio
import logging
from typing import TYPE_CHECKING, Callable, List, Union

import websockets

from .data import Context
from .base import BotBase

if TYPE_CHECKING:
    from .bot import QQbot

logger = logging.getLogger(__name__)


class ReceiveUnit(BotBase):
    plugin: List[Callable[['QQbot', Context], None]] = []

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def __enter__(self) -> 'ReceiveUnit':
        super().__enter__()
        return self

    def addFunction(
        self,
        func: Callable[['QQbot', Context], None],
    ) -> None:
        logger.debug(f"add function: {func.__name__ }")
        self.plugin.append(func)

    async def _receiver(self) -> None:
        logger.info(f"connect with ws://{self.socket}/message?...")
        async with websockets.connect(
                f"ws://{self.socket}/message?sessionKey={self.session}"
        ) as websocket:
            async for message in websocket:
                asyncio.create_task(self._solve(message))

    async def _solve(self, message: Union[str, bytes]) -> None:
        if isinstance(message, bytes):
            logger.error(f"get byte message {message}")
            return
        # TODO: low performance. should use 'run_in_executor'
        logger.debug(f"get: {message}")
        for func in self.plugin:
            try:
                func(self._bot, Context(message))
            except Exception as err:
                logger.exception(
                    f"receive module: {func.__name__}\n {message}")

    # TODO event