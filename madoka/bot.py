from __future__ import absolute_import

import asyncio
import logging
from typing import Optional

from websockets import ConnectionClosedError

from .register import getRegister, getEventRegistered, getScheduleRegistered
from .receive import ReceiveUnit
from .send import SendUnit
from .schedule import ScheduleUnit
from .asynchro import AsyncUnit
from .exception import MadokaInitError, MadokaRuntimeError

logger = logging.getLogger(__name__)


class QQbot(ReceiveUnit, SendUnit, ScheduleUnit, AsyncUnit):
    def __init__(
        self,
        qid: int,
        socket: str,
        authKey: str,
        autoRegister: bool = True,
        waitMirai: Optional[int] = None,
    ) -> None:
        super().__init__(
            qid=qid,
            socket=socket,
            authKey=authKey,
            waitMirai=waitMirai,
            bot=self,
        )
        self._autoRegister = autoRegister

    def __enter__(self) -> 'QQbot':
        try:
            logger.info(f"bot start: QQ={self.qid}")
            super().__enter__()
            return self
        except Exception as err:
            logger.critical("Bot initialization failed")
            raise MadokaInitError("__enter__") from err

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        catch = super().__exit__(exc_type, exc_value, traceback)
        if exc_type is KeyboardInterrupt:
            logger.info("exit because of KeyboardInterrupt")
            return True
        # elif exc_type and exc_type.__cause__ is KeyboardInterrupt:
        #     logger.info("exit because of KeyboardInterrupt")
        #     return True
        elif exc_type:
            logger.critical(f"QQbot crashed: qid={self.qid}")
        else:
            logger.info(f"QQbot exit: qid={self.qid}")
        return catch

    def working(self) -> None:
        """
        start working
        """
        if self._autoRegister:
            for func in getRegister():
                self.addFunction(func)
            for type, func in getEventRegistered():
                self.addEvent(type, func)
            for task in getScheduleRegistered():
                self.addTimeTask(task)

        # event loop
        try:
            self._loop.run_until_complete(self._main())
        finally:
            logger.info('shutdown all tasks')
            for task in asyncio.Task.all_tasks():
                task.cancel()
            self._loop.run_until_complete(self._loop.shutdown_asyncgens())
            self._loop.run_until_complete(asyncio.sleep(0.5))
            self._loop.close()

    async def _main(self):
        logger.info("bot start working")
        try:
            await asyncio.gather(
                self._receiver(),
                self._sender(),
                self._schedule(),
                self._asyncTask(),
            )
        except asyncio.CancelledError:
            logger.debug("main task cancelled")
        except ConnectionClosedError as err:
            logger.error(f"websockets connection closed")
            raise MadokaRuntimeError("websockets connection closed") from err
        except Exception as err:
            logger.exception(f"{err.__class__.__name__}':")
            raise MadokaRuntimeError() from err
