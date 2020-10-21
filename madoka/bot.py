from __future__ import absolute_import

import asyncio
import logging

from websockets import ConnectionClosedError

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
        self._autoRegister = autoRegister
        self._hasError = False

    def __enter__(self) -> 'QQbot':
        # TODO when initialization failed, bot shouldn't continue running.
        try:
            logger.info(f"bot start: QQ={self.qid}")
            super().__enter__()
        except:
            logger.critical("Bot initialization failed")
            self._hasError = True
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        if self._hasError:
            logger.debug("bot has error, skip release")
            return True
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
        if self._hasError:
            logger.error("bot has error, skip running")
            return

        if self._autoRegister:
            for func in getRegister():
                self.addFunction(func)
            for type, func in getEventRegistered():
                self.addEvent(type, func)
            for task in getScheduleRegistered():
                self.addTimeTask(task)

        # event loop
        self._loop.run_until_complete(self._main())
        self._loop.run_until_complete(self._loop.shutdown_asyncgens())
        self._loop.close()

    async def _main(self):
        def cancel():
            for t in tasks:
                t.cancel()

        logger.info("bot start working")
        tasks = list(
            map(asyncio.ensure_future, [
                self._receiver(),
                self._sender(),
                self._schedule(),
                self._asyncTask(),
            ]))
        try:
            await asyncio.gather(*tasks)
        except ConnectionClosedError:
            logger.error(f"websockets connection closed")
            cancel()
        except Exception as err:
            logger.exception(f"{err.__class__.__name__}':")
            cancel()
