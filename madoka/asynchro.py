from __future__ import absolute_import

import logging
from typing import Coroutine

from .base import BotBase

logger = logging.getLogger(__name__)

# TODO add simple AsyncTask interface using aiohttp


class AsyncUnit(BotBase):
    def addAsyncTask(self, coroutine: Coroutine) -> None:
        async def catchError(coroutine: Coroutine):
            try:
                await coroutine
            except:
                logger.exception(f"asynchro module: {coroutine.__name__}")

        logger.debug(f"asynchronous task: {coroutine.__name__}")
        self._loop.create_task(catchError(coroutine))
