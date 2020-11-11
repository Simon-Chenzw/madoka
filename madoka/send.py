from __future__ import absolute_import

import asyncio
import logging
from typing import (Any, Callable, Coroutine, Dict, Iterable, Literal,
                    Optional, Union)

import aiohttp

from .base import BotBase
from .data import (Context, FriendSender, GroupSender, PlainText, Sender,
                   TempSender, Text)

logger = logging.getLogger(__name__)


class SendUnit(BotBase):
    def __enter__(self) -> 'SendUnit':
        super().__enter__()
        self._sendQueue: 'asyncio.Queue[Coroutine]' = asyncio.Queue(
            loop=self._loop)
        return self

    def send(
        self,
        method: Literal["get", "post"],
        interface: str,
        data: Dict[str, Any],
        callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> None:
        """
        auto add sessionKey
        :data: will transform to json
        :callback: get json response
        """
        logger.debug(f"send call: {method} {interface} {data}")
        data['sessionKey'] = self._session
        if method == "get":
            self._sendQueue.put_nowait(
                self._asyncget(interface, data, callback))
        elif method == "post":
            self._sendQueue.put_nowait(
                self._asyncpost(interface, data, callback))

    async def _asyncget(
        self,
        interface: str,
        data: Dict[str, Any],
        callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> None:
        logger.info(f"{interface} [GET]: {data}")
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"http://{self._socket}/{interface}",
                    params=data,
            ) as res:
                js = await res.json()
                logger.debug(f"{interface} response [{res.status}]: {js}")
                try:
                    if callback: callback(js)
                except Exception as err:
                    logger.exception(f"callback {callback.__name__} failed:")

    async def _asyncpost(
        self,
        interface: str,
        data: Dict[str, Any],
        callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> None:
        logger.info(f"{interface} [POST]: {data}")
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f"http://{self._socket}/{interface}",
                    json=data,
            ) as res:
                js = await res.json()
                logger.debug(f"{interface} response [{res.status}]: {js}")
                try:
                    if callback: callback(js)
                except Exception as err:
                    logger.exception(f"callback {callback.__name__} failed:")

    async def _sender(self) -> None:
        logger.info(f"waiting for send")
        while True:
            task = await self._sendQueue.get()
            self._loop.create_task(task)
            self._sendQueue.task_done()

    # special send method is below

    @staticmethod
    def _toMessageChain(message: Union[str, Text, Iterable['Text']]) -> Any:
        if isinstance(message, str):
            return [PlainText(message).json]
        elif isinstance(message, Text):
            return [message.json]
        else:
            return [m.json for m in message]

    def reply(
        self,
        sender: Sender,
        message: Union[str, Text, Iterable['Text']],
        quoteId: Optional[int] = None,
    ) -> None:
        if isinstance(sender, FriendSender):
            self.sendFriendMessage(
                target=sender.id,
                message=message,
                quote=quoteId,
            )
        elif isinstance(sender, GroupSender):
            self.sendGroupMessage(
                target=sender.groupId,
                message=message,
                quote=quoteId,
            )
        elif isinstance(sender, TempSender):
            self.sendTempMessage(
                target=sender.id,
                group=sender.groupId,
                message=message,
                quote=quoteId,
            )

    def quote(
        self,
        context: Context,
        message: Union[str, Text, Iterable['Text']],
    ) -> None:
        self.reply(
            sender=context.sender,
            message=message,
            quoteId=context.messageId,
        )

    def sendFriendMessage(
        self,
        target: int,
        message: Union[str, Text, Iterable['Text']],
        quote: Optional[int] = None,
    ) -> None:
        """
        /sendFriendMessage
        """
        data = {
            "target": target,
            "messageChain": self._toMessageChain(message),
        }
        if quote: data['quote'] = quote
        self.send(
            method="post",
            interface='sendFriendMessage',
            data=data,
        )

    def sendGroupMessage(
        self,
        target: int,
        message: Union[str, Text, Iterable['Text']],
        quote: Optional[int] = None,
    ) -> None:
        """
        /sendGroupMessage
        """
        data = {
            "target": target,
            "messageChain": self._toMessageChain(message),
        }
        if quote: data['quote'] = quote
        self.send(
            method="post",
            interface='sendGroupMessage',
            data=data,
        )

    def sendTempMessage(
        self,
        target: int,
        group: int,
        message: Union[str, Text, Iterable['Text']],
        quote: Optional[int] = None,
    ) -> None:
        """
        /sendTempMessage
        """
        data = {
            "qq": target,
            "group": group,
            "messageChain": self._toMessageChain(message),
        }
        if quote: data['quote'] = quote
        self.send(
            method="post",
            interface='sendTempMessage',
            data=data,
        )

    def messageFromId(
        self,
        messageId: int,
        callback: Callable[[Context], None],
        failedCallback: Optional[Callable] = None,
    ) -> None:
        """
        /messageFromId
        """
        def trans(json: Dict[str, Any]):
            if json['code']:
                logger.error(
                    f"messageFromId failed: code={json['code']} {json['msg']}")
                if failedCallback:
                    failedCallback()
            else:
                callback(Context(json['data']))

        self.send(
            method="get",
            interface="messageFromId",
            data={"id": messageId},
            callback=trans,
        )

    # TODO more method
