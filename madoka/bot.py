from __future__ import absolute_import

import asyncio
import logging

from .register import getRegister, getEventRegistered, getScheduleRegistered
from .receive import ReceiveUnit
from .send import SendUnit
from .schedule import ScheduleUnit
from .asynchro import AsyncUnit

logger = logging.getLogger(__name__)


class QQbot(ReceiveUnit, SendUnit, ScheduleUnit, AsyncUnit):
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
            bot=self,
        )
        self.autoRegister = autoRegister

    def __enter__(self) -> 'QQbot':
        # TODO when initialization failed, bot shouldn't continue running.
        try:
            logger.info(f"bot start: QQ={self.qid}")
            super().__enter__()
        except:
            logger.critical("Bot initialization failed")
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        catch = super().__exit__(exc_type, exc_value, traceback)
        if exc_type is KeyboardInterrupt:
            logger.info("exit because of KeyboardInterrupt")
            return True
        elif exc_type:
            logger.critical(f"QQbot crashed: qid={self.qid}")
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
            for type, func in getEventRegistered():
                self.addEvent(type, func)
            for task in getScheduleRegistered():
                self.addTimeTask(task)

        # event loop
        logger.info("bot start working")
        self.loop.run_until_complete(
            asyncio.gather(
                self._receiver(),
                self._sender(),
                self._schedule(),
                self._asyncTask(),
            ))
        # It seem needn't to run this, because bot only exited by exceptions
        # self.loop.run_until_complete(self.loop.shutdown_asyncgens())
        # self.loop.close()
