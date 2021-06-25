from __future__ import annotations

import asyncio
import json
import logging
from itertools import count
from typing import (TYPE_CHECKING, Any, AsyncGenerator, Coroutine, Literal,
                    Optional)

from cachetools import TTLCache
from websockets.exceptions import ConnectionClosedError
from websockets.legacy import client

if TYPE_CHECKING:
    from .bot import QQbot

logger = logging.getLogger(__name__)

MAX_QUEUE_SIZE = 10000


class FutureCache(TTLCache[str, asyncio.Future[dict[str, Any]]]):
    def popitem(self):
        k, v = super().popitem()
        logger.warning(f"Receive response timeout syncId={k}")
        v.set_exception(TimeoutError("Receive response timeout"))
        return k, v


class BotBase:
    def __init__(
        self,
        qid: int,
        host: str,
        verifyKey: str,
        adminQid: Optional[int] = None,
        waitMirai: Optional[int] = None,
        channel: Literal['message', 'event', 'all'] = 'all',
        protocol: Literal['ws', 'wss'] = 'ws',
        reservedSyncId: int = -1,
    ) -> None:
        self.qid = qid
        self.adminQid = adminQid
        self._waitMirai = waitMirai
        self._reservedSyncId = str(reservedSyncId)
        self._wsurl = f"{protocol}://{host}/{channel}?verifyKey={verifyKey}&qq={qid}"

        self._curSyncId = count()
        self._futures = FutureCache(maxsize=10000, ttl=3600)
        self._tasks: list[asyncio.Task] = []

        # self._bot just use for typing hinting
        self._bot: QQbot = self  # type: ignore

    async def __aenter__(self) -> BotBase:
        logger.debug("Connect to Websocket Adapter")
        await self._wsconnect()
        self._session = json.loads(await self._ws.recv())['data']['session']
        logger.info(f"successfully connect: sessionKey={self._session}")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        logger.debug("Disconnect to Websocket Adapter")
        await self._ws.close()
        return False

    async def _wsconnect(self) -> None:
        self._connect = client.Connect(self._wsurl)
        if self._waitMirai is None:
            self._waitMirai = 1
        cnt = 0
        while not (cnt and cnt == self._waitMirai):
            try:
                cnt += 1
                self._ws = await self._connect
            except:
                if self._waitMirai != 1:
                    logger.debug(f"get api information failed: {cnt} times")
                if cnt != self._waitMirai:
                    await asyncio.sleep(3)
                else:
                    logger.error("Unable to connect to mirai-api-http")
                    raise
            else:
                if cnt != 1: await asyncio.sleep(3)
                break

    def send(
        self,
        command: str,
        subCommand: Optional[str],
        content: dict[str, Any],
    ) -> asyncio.Future[dict[str, Any]]:
        syncId = str(next(self._curSyncId))
        data = json.dumps({
            "syncId": syncId,
            "command": command,
            "subCommand": subCommand,
            "content": content
        })
        logger.info(f"[{command}] {subCommand}: {content}")
        self._futures[syncId] = asyncio.Future()
        asyncio.create_task(self._ws.send(data))
        return self._futures[syncId]

    async def _recv(self) -> AsyncGenerator[dict[str, Any], None]:
        logger.debug("Start receiving")
        while True:
            resp = json.loads(await self._ws.recv())
            syncId: str = resp['syncId']
            data: dict[str, Any] = resp['data']
            if syncId == self._reservedSyncId:
                logger.info(f"Received: {data=}")
                yield data
            else:
                future = self._futures.pop(syncId, None)
                if future:
                    logger.debug(f"Response: {syncId=} {data=}")
                    future.set_result(data)
                else:
                    logger.debug(f"Response: {syncId=} {data=}")

    def _startTask(self, cor: Coroutine[None, None, None]) -> asyncio.Task:
        task = asyncio.create_task(cor)
        self._tasks.append(task)
        return task

    async def wait(self) -> None:
        logger.debug("Wating for all tasks")
        try:
            await asyncio.gather(*self._tasks)
        except asyncio.CancelledError:
            logger.debug("Task cancelled")
        except ConnectionClosedError:
            logger.error(f"websockets connection closed")
            raise RuntimeError("websockets connection closed") from None

    def stop(self) -> None:
        logger.info(f"Stoping Bot {self.qid}")
        for task in self._tasks:
            task.cancel()
