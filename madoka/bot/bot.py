from __future__ import annotations

import asyncio
import logging
from typing import Awaitable, List, Optional

from websockets import ConnectionClosedError

from ..register import context, event, timed
from .exception import MadokaInitError, MadokaRuntimeError
from .receive import ReceiveUnit
from .schedule import ScheduleUnit
from .send import SendUnit

logger = logging.getLogger('madoka')


# TODO and plugin util: support reload
class QQbot(ReceiveUnit, SendUnit, ScheduleUnit):
    def __enter__(self) -> 'QQbot':
        try:
            logger.info(f"bot start: QQ={self.qid}")
            super().__enter__()
            return self
        except MadokaInitError:
            logger.error("Bot initialization failed")
            raise
        except:
            logger.error("Bot initialization failed")
            raise MadokaInitError("__enter__")

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        catch = super().__exit__(exc_type, exc_value, traceback)
        if exc_type is KeyboardInterrupt:
            logger.info("exit because of KeyboardInterrupt")
            catch = True
        elif exc_type:
            logger.critical(f"QQbot crashed: qid={self.qid}")
        else:
            logger.info(f"QQbot exit: qid={self.qid}")
        return catch

    def working(
        self,
        main_task: Optional[Awaitable] = None,
        enable_receiver: bool = True,
        enable_schedule: bool = True,
    ) -> None:
        """
        start working, will blocking forever unless revceiver==schedule==False
        :main_task: Coroutine that need to be executed at the same time
        """
        # TODO More detail
        if self._autoRegister:
            for func in context.getRegistered():
                self.addFunction(func)
            for type, func in event.getRegistered():
                self.addEvent(type, func)
            for func, schedule in timed.getRegistered():
                self.addTimedTask(func, schedule)

        lst = []
        if main_task is not None: lst.append(main_task)
        if enable_receiver: lst.append(self._receiver())
        if enable_schedule: lst.append(self._schedule())

        # event loop
        try:
            self._loop.run_until_complete(self._main(lst))
        except KeyboardInterrupt:
            self.stop()
        finally:
            self._loop.run_until_complete(self._loop.shutdown_asyncgens())
            self._loop.run_until_complete(asyncio.sleep(0.5))
            self._loop.close()

    def stop(self):
        logger.info("stopping the bot")
        self._mainTask.cancel()

    async def _main(self, gather_list: List[Awaitable]):
        logger.info("bot start working")
        if len(gather_list) == 0:
            raise MadokaRuntimeError('Nothing to do')
        try:
            self._mainTask = asyncio.gather(*gather_list)
            await self._mainTask
        except asyncio.CancelledError:
            logger.debug("main task cancelled")
        except ConnectionClosedError as err:
            logger.error(f"websockets connection closed")
            raise MadokaRuntimeError("websockets connection closed")
        except Exception as err:
            logger.exception(f"{err.__class__.__name__}':")
            raise MadokaRuntimeError()
