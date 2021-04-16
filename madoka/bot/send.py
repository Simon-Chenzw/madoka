from __future__ import annotations

import logging
from asyncio import Task
from typing import Any, Dict, Iterable, List, Optional, Union

import aiohttp

from ..typing import (Context, FriendSender, GroupSender, PlainText, Sender,
                      TempSender, Text)
from .base import BotBase
from .exception import MadokaRuntimeError
from .receive import contextStore

logger = logging.getLogger('madoka')


class SendUnit(BotBase):
    def apiGet(
        self,
        interface: str,
        data: Dict[str, Any],
    ) -> Task[Dict[str, Any]]:
        """
        auto add sessionKey
        :data: will transform to params
        """
        return self.create_task(self.asyncApiGet(interface, data))

    def apiPost(
        self,
        interface: str,
        data: Dict[str, Any],
    ) -> Task[Dict[str, Any]]:
        """
        auto add sessionKey
        :data: will transform to json
        """
        return self.create_task(self.asyncApiPost(interface, data))

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
    ) -> Task[Dict[str, Any]]:
        if self.adminQid:
            return self.sendFriendMessage(
                target=self.adminQid,
                message=message,
            )
        else:
            raise MadokaRuntimeError('adminQid is not initialized')

    def reply(
        self,
        message: Union[str, Text, Iterable['Text']],
        quoteId: Optional[int] = None,
    ) -> Task[Dict[str, Any]]:
        sender = contextStore.get().sender
        if isinstance(sender, FriendSender):
            logger.debug(f"reply to {sender.nickname} {sender.id}")
            return self.sendFriendMessage(
                target=sender.id,
                message=message,
                quote=quoteId,
            )
        elif isinstance(sender, GroupSender):
            logger.debug(f"reply to {sender.memberName} {sender.id}")
            return self.sendGroupMessage(
                target=sender.group.id,
                message=message,
                quote=quoteId,
            )
        elif isinstance(sender, TempSender):
            logger.debug(f"reply to {sender.memberName} {sender.id}")
            return self.sendTempMessage(
                target=sender.id,
                group=sender.group.id,
                message=message,
                quote=quoteId,
            )
        else:
            raise MadokaRuntimeError('Unknown Sender Type')

    def quoteReply(
        self,
        message: Union[str, Text, Iterable['Text']],
    ) -> Task[Dict[str, Any]]:
        messageId = contextStore.get().messageId
        logger.debug(f"quote reply to messageId={messageId}")
        return self.reply(
            message=message,
            quoteId=messageId,
        )

    @staticmethod
    def _formatMessage(message: Union[str, Text, Iterable['Text']]) -> List[Dict[str,Any]]:
        if isinstance(message, str):
            return [PlainText(message).dict()]
        elif isinstance(message, Text):
            return [message.dict()]
        else:
            try:
                return [text.dict() for text in message]
            except:
                logger.exception(
                    f"format error: {message.__class__.__name__=}")
                raise

    def sendFriendMessage(
        self,
        target: int,
        message: Union[str, Text, Iterable['Text']],
        quote: Optional[int] = None,
    ) -> Task[Dict[str, Any]]:
        """
        /sendFriendMessage
        """
        data = {
            "target": target,
            "messageChain": self._formatMessage(message),
        }
        if quote: data['quote'] = quote
        return self.apiPost(interface='sendFriendMessage', data=data)

    def sendGroupMessage(
        self,
        target: int,
        message: Union[str, Text, Iterable['Text']],
        quote: Optional[int] = None,
    ) -> Task[Dict[str, Any]]:
        """
        /sendGroupMessage
        """
        data = {
            "target": target,
            "messageChain": self._formatMessage(message),
        }
        if quote: data['quote'] = quote
        return self.apiPost(interface='sendGroupMessage', data=data)

    def sendTempMessage(
        self,
        target: int,
        group: int,
        message: Union[str, Text, Iterable['Text']],
        quote: Optional[int] = None,
    ) -> Task[Dict[str, Any]]:
        """
        /sendTempMessage
        """
        data = {
            "qq": target,
            "group": group,
            "messageChain": self._formatMessage(message),
        }
        if quote: data['quote'] = quote
        return self.apiPost(interface='sendTempMessage', data=data)

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
                return Context.parse_obj(json['data'])
            else:
                logger.error(
                    f"messageFromId failed: code={json['code']} {json['msg']}")
        except:
            pass

    # TODO more method
