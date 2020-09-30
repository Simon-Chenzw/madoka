from __future__ import absolute_import

import asyncio
import logging
from typing import TYPE_CHECKING, Callable, List, Union

import websockets

from ..data import Context
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
        logger.info(f"add function: {func.__name__ }")
        self.plugin.append(func)

    async def _receiver(self, bot: 'QQbot') -> None:
        logger.info(f"start listen ws://{self.socket}/message?...")
        async with websockets.connect(
                f"ws://{self.socket}/message?sessionKey={self.session}"
        ) as websocket:
            async for message in websocket:
                asyncio.create_task(self._solve(bot, message))

    async def _solve(self, bot: 'QQbot', message: Union[str, bytes]) -> None:
        if isinstance(message, bytes):
            logger.warn(f"get byte message {message}")
            return
        # TODO: low performance. should use 'run_in_executor'
        logger.debug(f"get: {message}")
        for func in self.plugin:
            try:
                func(bot, Context(message))
            except Exception as err:
                logger.warn(
                    f"{func.__name__}: '{err.__class__.__name__}' {err} \n{message}"
                )

    # TODO event