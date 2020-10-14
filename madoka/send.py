from __future__ import absolute_import

import asyncio
import logging
from typing import Any, Callable, Coroutine, Optional, Union, Literal

import aiohttp

from .base import BotBase
from .data import FriendSender, GroupSender, MessageChain, PlainText, Sender, TempSender, Text

logger = logging.getLogger(__name__)


class SendUnit(BotBase):
    def __enter__(self) -> 'SendUnit':
        super().__enter__()
        self._sendQueue: 'asyncio.Queue[Coroutine]' = asyncio.Queue(
            loop=self.loop)
        return self

    def send(
        self,
        method: Literal["get", "post"],
        interface: str,
        data: Any,
        callback: Optional[Callable[[Any], None]] = None,
    ) -> None:
        """
        auto add sessionKey
        :data: will transform to json
        :callback: get json response
        """
        logger.debug(f"send call: {method} {interface} {data}")
        if method == "get":
            self._sendQueue.put_nowait(
                self._asyncget(interface, data, callback))
        elif method == "post":
            self._sendQueue.put_nowait(
                self._asyncpost(interface, data, callback))

    async def _asyncget(
        self,
        interface: str,
        data: Any,
        callback: Optional[Callable[[Any], None]] = None,
    ) -> None:
        data['sessionKey'] = self.session
        logger.info(f"{interface} [GET]: {data}")
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"http://{self.socket}/{interface}",
                    params=data,
            ) as res:
                js = await res.json()
                logger.debug(f"{interface} response: {res}")
                if js['code']:
                    logger.error(f"send error: code={js['code']}")
                elif callback:
                    try:
                        callback(js)
                    except Exception as err:
                        logger.exception(
                            f"callback {callback.__name__} failed:")

    async def _asyncpost(
        self,
        interface: str,
        data: Any,
        callback: Optional[Callable[[Any], None]] = None,
    ) -> None:
        data['sessionKey'] = self.session
        logger.info(f"{interface} [POST]: {data}")
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f"http://{self.socket}/{interface}",
                    json=data,
            ) as res:
                js = await res.json()
                logger.debug(f"{interface} response: {res}")
                if js['code']:
                    logger.error(f"send error: code={js['code']}")
                elif callback:
                    try:
                        callback(js)
                    except Exception as err:
                        logger.exception(
                            f"callback {callback.__name__} failed:")

    async def _sender(self) -> None:
        logger.info(f"waiting for send")
        while True:
            task = await self._sendQueue.get()
            try:
                await task
            except Exception as err:
                logger.exception("send failed:")
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
            method="post",
            interface='sendFriendMessage',
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
            method="post",
            interface='sendGroupMessage',
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
            method="post",
            interface='sendTempMessage',
            data={
                "qq": target,
                "group": group,
                "messageChain": self._toMessageChain(message),
            },
        )

    def messageFromId(
        self,
        messageId: int,
        callback: Callable[[Any], None],
    ) -> None:
        """
        /messageFromId
        """
        self.send(
            method="get",
            interface="messageFromId",
            data={"id": messageId},
            callback=callback,
        )

    # TODO more method
