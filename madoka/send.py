from __future__ import absolute_import

import asyncio
import logging
from typing import Any, Coroutine, Union

import aiohttp

from .base import BotBase
from .data import (FriendSender, GroupSender, MessageChain, PlainText, Sender,
                   TempSender, Text)

logger = logging.getLogger(__name__)


class SendUnit(BotBase):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def __enter__(self) -> 'SendUnit':
        super().__enter__()
        self._sendQueue: 'asyncio.Queue[Coroutine[Any, Any,int]]' = asyncio.Queue(
            loop=self.loop)
        return self

    def send(self, method: str, data: Any) -> None:
        """
        auto add sessionKey
        :data: will transform to json
        """
        logger.info(f"send call: {method} {data}")
        self._sendQueue.put_nowait(self._asyncsend(method, data))

    async def _asyncsend(self, method: str, data: Any) -> int:
        data['sessionKey'] = self.session
        logger.debug(f"send: {method} {data}")
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f"http://{self.socket}/{method}",
                    json=data,
            ) as res:
                js = await res.json()
                return js['code']

    async def _sender(self) -> None:
        logger.info(f"waiting for send")
        while True:
            task = await self._sendQueue.get()
            ret = await task
            if ret:
                logger.warn(f"send error: code={ret}")
            self._sendQueue.task_done()

    # special send method is below

    @staticmethod
    def _toMessageChain(message: Union[str, Text, MessageChain]) -> Any:
        if isinstance(message, str):
            return [PlainText(message).js]
        elif isinstance(message, Text):
            return [message.js]
        else:
            return [m.js for m in message]

    def reply(
        self,
        sender: Sender,
        message: Union[str, Text, MessageChain],
    ) -> None:
        if isinstance(sender, FriendSender):
            self.sendFriendMessage(
                target=sender.id,
                message=message,
            )
        elif isinstance(sender, GroupSender):
            self.sendGroupMessage(
                target=sender.groupId,
                message=message,
            )
        elif isinstance(sender, TempSender):
            self.sendTempMessage(
                target=sender.id,
                group=sender.groupId,
                message=message,
            )

    def sendFriendMessage(
        self,
        target: int,
        message: Union[str, Text, MessageChain],
    ) -> None:
        """
        /sendFriendMessage
        """
        self.send(
            method='sendFriendMessage',
            data={
                "target": target,
                "messageChain": self._toMessageChain(message),
            },
        )

    def sendGroupMessage(
        self,
        target: int,
        message: Union[str, Text, MessageChain],
    ) -> None:
        """
        /sendGroupMessage
        """
        self.send(
            method='sendGroupMessage',
            data={
                "target": target,
                "messageChain": self._toMessageChain(message),
            },
        )

    def sendTempMessage(
        self,
        target: int,
        group: int,
        message: Union[str, Text, MessageChain],
    ) -> None:
        """
        /sendTempMessage
        """
        self.send(
            method='sendTempMessage',
            data={
                "qq": target,
                "group": group,
                "messageChain": self._toMessageChain(message),
            },
        )

    # TODO more method