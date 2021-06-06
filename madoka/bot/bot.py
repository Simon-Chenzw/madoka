from __future__ import annotations

import asyncio
import logging

from .api import ApiUnit
from .schedule import ScheduleUnit
from .solve import SolveUnit

logger = logging.getLogger(__name__)


class QQbot(ApiUnit, ScheduleUnit, SolveUnit):
    def __enter__(self) -> None:
        raise TypeError("Use 'async with' instead")

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        return False

    async def __aenter__(self) -> QQbot:
        logger.info(f"bot start: QQ={self.qid}")
        await super().__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        catch = await super().__aexit__(exc_type, exc_val, exc_tb)
        if exc_type:
            logger.critical(f"QQbot crashed: qid={self.qid}")
        else:
            logger.info(f"QQbot exit: qid={self.qid}")
        return catch

    async def start(
        self,
        *,
        block: bool = True,
        receive: bool = True,
        schedule: bool = True,
    ):
        if receive: self._startTask(self._solve())
        if schedule: self._startTask(self._schedule())
        if block:
            await self.wait()

    def simple_running(self) -> None:
        async def main():
            async with self as bot:
                await bot.start()

        logger.info("Simple running bot")
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            logger.info("exit because of KeyboardInterrupt")
