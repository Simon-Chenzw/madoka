from __future__ import absolute_import

import asyncio
import logging
from typing import Coroutine

from .base import BotBase

logger = logging.getLogger(__name__)


class AsyncUnit(BotBase):
    def __enter__(self) -> 'AsyncUnit':
        super().__enter__()
        self._asyncTaskQueue: 'asyncio.Queue[Coroutine]' = asyncio.Queue(
            loop=self.loop)
        return self

    def addAsyncTask(self, task: Coroutine) -> None:
        logger.debug(f"add asynchronous task: {task.__name__}")
        self._asyncTaskQueue.put_nowait(task)

    async def _asyncTask(self):
        logger.info("waiting for asynchronous task")
        while True:
            task = await self._asyncTaskQueue.get()
            logger.debug(f"asynchronous task: {task.__name__}")
            try:
                await task
            except Exception as err:
                logger.warn(f"{task.__name__} {err.__class__.__name__}: {err}")
            finally:
                self._asyncTaskQueue.task_done()
