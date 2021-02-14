from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, Optional, Union

import aiohttp

from ..typing import (Context, FriendSender, GroupSender, PlainText, Sender,
                      TempSender, Text)
from .base import BotBase
from .exception import MadokaRuntimeError

logger = logging.getLogger('madoka')


class SendUnit(BotBase):
    def apiGet(
        self,
        interface: str,
        data: Dict[str, Any],
    ) -> None:
        """
        auto add sessionKey
        :data: will transform to params
        """
        self.create_task(self.asyncApiGet(interface, data))

    def apiPost(self, interface: str, data: Dict[str, Any]) -> None:
        """
        auto add sessionKey
        :data: will transform to json
        """
        self.create_task(self.asyncApiPost(interface, data))

    async def asyncApiGet(
        self,
        interface: str,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        auto add sessionKey
        :data: will transform to params
        """
        logger.info(f"{interface} [GET]: {data}")
        data['sessionKey'] = self._session
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"http://{self._socket}/{interface}",
                    params=data,
            ) as resp:
                js = await resp.json()
                logger.debug(f"{interface} response [{resp.status}]: {js}")
                return js

    async def asyncApiPost(
        self,
        interface: str,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        auto add sessionKey
        :data: will transform to json
        """
        logger.info(f"{interface} [POST]: {data}")
        data['sessionKey'] = self._session
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f"http://{self._socket}/{interface}",
                    json=data,
            ) as resp:
                js = await resp.json()
                logger.debug(f"{interface} response [{resp.status}]: {js}")
                return js

    # special send method is below

    def sendToAdmin(
        self,
        message: Union[str, Text, Iterable['Text']],
    ) -> None:
        if self.adminQid:
            self.sendFriendMessage(target=self.adminQid, message=message)
        else:
            raise MadokaRuntimeError('adminQid is not initialized')

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

    def quoteReply(
        self,
        context: Context,
        message: Union[str, Text, Iterable['Text']],
    ) -> None:
        self.reply(
            sender=context.sender,
            message=message,
            quoteId=context.messageId,
        )

    @staticmethod
    def _formatMessage(message: Union[str, Text, Iterable['Text']]) -> Any:
        if isinstance(message, str):
            return [PlainText(message).serialize]
        elif isinstance(message, Text):
            return [message.serialize]
        else:
            try:
                return [text.serialize for text in message]
            except:
                logger.exception(
                    f"format error: {message.__class__.__name__=}")
                raise

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
            "messageChain": self._formatMessage(message),
        }
        if quote: data['quote'] = quote
        self.apiPost(interface='sendFriendMessage', data=data)

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
            "messageChain": self._formatMessage(message),
        }
        if quote: data['quote'] = quote
        self.apiPost(interface='sendGroupMessage', data=data)

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
            "messageChain": self._formatMessage(message),
        }
        if quote: data['quote'] = quote
        self.apiPost(interface='sendTempMessage', data=data)

    async def messageFromId(self, messageId: int) -> Optional[Context]:
        """
        /messageFromId
        """
        try:
            json = await self.asyncApiGet(
                interface="messageFromId",
                data={"id": messageId},
            )
            if json['code'] == 0:
                return Context(json['data'])
            else:
                logger.error(
                    f"messageFromId failed: code={json['code']} {json['msg']}")
        except:
            pass

    # TODO more method
