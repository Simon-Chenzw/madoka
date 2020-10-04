from __future__ import absolute_import

import asyncio
import logging

from .register import getRegister, getScheduleRegistered
from .receive import ReceiveUnit
from .schedule import ScheduleUnit
from .send import SendUnit

logger = logging.getLogger(__name__)


class QQbot(ReceiveUnit, SendUnit, ScheduleUnit):
    def __init__(
        self,
        qid: int,
        socket: str,
        authKey: str,
        autoRegister: bool = True,
    ) -> None:
        super().__init__(
            qid=qid,
            socket=socket,
            authKey=authKey,
        )
        self.autoRegister = autoRegister

    def __enter__(self) -> 'QQbot':
        logger.info(f"bot start: QQ={self.qid}")
        super().__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        catch = super().__exit__(exc_type, exc_value, traceback)
        if exc_type is KeyboardInterrupt:
            logger.info("exit because of KeyboardInterrupt")
            return True
        elif exc_type:
            logger.error(f"QQbot crashed: qid={self.qid}")
        else:
            logger.info(f"QQbot exit: qid={self.qid}")
        return catch

    def working(self) -> None:
        """
        start working
        """

        if self.autoRegister:
            for func in getRegister():
                self.addFunction(func)
            for task in getScheduleRegistered():
                self.addTimeTask(task)

        # event loop
        logger.info("start event loop")
        self.loop.run_until_complete(
            asyncio.gather(
                self._receiver(bot=self),
                self._sender(),
                self._schedule(bot=self),
            ))
        # It seem needn't to run this, because bot only exited by exceptions
        # self.loop.run_until_complete(self.loop.shutdown_asyncgens())
        # self.loop.close()
