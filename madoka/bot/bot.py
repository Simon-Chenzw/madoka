from __future__ import annotations

import asyncio
import logging
from typing import Optional

from websockets import ConnectionClosedError

from ..register import context, event, timed
from .exception import MadokaInitError, MadokaRuntimeError
from .receive import ReceiveUnit
from .schedule import ScheduleUnit
from .send import SendUnit

logger = logging.getLogger('madoka')


# TODO and plugin util: support reload
class QQbot(ReceiveUnit, SendUnit, ScheduleUnit):
    def __init__(
        self,
        qid: int,
        socket: str,
        authKey: str,
        messageReception: bool = True,
        autoRegister: bool = True,
        adminQid: Optional[int] = None,
        waitMirai: Optional[int] = None,
    ) -> None:
        """
        :qid: Bot's QQ
        :socket: ip & port
        :authKey: mirai-api-http authKey
        :messageReception: activate message reception
        :autoRegister: automatically add all registered function
        :waitMirai: Retry after connection failure during initialization, Zero means infinity, None means None.
        """
        super().__init__(
            qid=qid,
            socket=socket,
            authKey=authKey,
            bot=self,
            adminQid=adminQid,
            waitMirai=waitMirai,
        )
        self._autoRegister = autoRegister
        self.messageReception = messageReception

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

    def working(self) -> None:
        """
        start working
        """
        # TODO More detail
        if self._autoRegister:
            for func in context.getRegistered():
                self.addFunction(func)
            for type, func in event.getRegistered():
                self.addEvent(type, func)
            for func, schedule in timed.getRegistered():
                self.addTimedTask(func, schedule)

        # event loop
        try:
            self._loop.run_until_complete(self._main())
        except KeyboardInterrupt:
            self.stop()
        finally:
            self._loop.run_until_complete(self._loop.shutdown_asyncgens())
            self._loop.run_until_complete(asyncio.sleep(0.5))
            self._loop.close()

    def stop(self):
        logger.info("stopping the bot")
        self._mainTask.cancel()

    async def _main(self):
        logger.info("bot start working")
        try:
            if self.messageReception:
                self._mainTask = asyncio.gather(
                    self._receiver(),
                    self._schedule(),
                )
            else:
                self._mainTask = asyncio.ensure_future(self._schedule())
            await self._mainTask
        except asyncio.CancelledError:
            logger.debug("main task cancelled")
        except ConnectionClosedError as err:
            logger.error(f"websockets connection closed")
            raise MadokaRuntimeError("websockets connection closed")
        except Exception as err:
            logger.exception(f"{err.__class__.__name__}':")
            raise MadokaRuntimeError()
