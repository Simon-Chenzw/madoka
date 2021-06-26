from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Iterable, Optional, Union

from ..typing import (Context, ForwardMessageNode, ForwardMessageText,
                      FriendSender, GroupSender, PlainText, TempSender, Text)
from .base import BotBase
from .solve import contextStore

logger = logging.getLogger(__name__)

Message = Union[str, Text, Iterable[Text]]
FutureRet = asyncio.Future[dict[str, Any]]


class ApiUnit(BotBase):
    @staticmethod
    def _formatMessage(message: Message) -> list[dict[str, Any]]:
        if isinstance(message, str):
            return [PlainText(message).dict()]
        elif isinstance(message, Text):
            return [message.dict()]
        else:
            return [text.dict() for text in message]

    def pack(
        self,
        msgs: list[Message],
        numero: bool = True,
    ) -> ForwardMessageText:
        """
        Fake a ForwardMessageText to pack in one Text
        """
        nodes: list[ForwardMessageNode] = []
        for i, msg in enumerate(msgs):
            if isinstance(msg, str):
                lst: list[Text] = [PlainText(msg)]
            elif isinstance(msg, Text):
                lst: list[Text] = [msg]
            else:
                lst: list[Text] = list(msg)
            name = self._name
            if numero:
                name += f" - {i+1}/{len(msgs)}"
            nodes.append(
                ForwardMessageNode(
                    senderId=self.qid,
                    time=int(time.time()),
                    senderName=name,
                    messageChain=lst,
                ))

        return ForwardMessageText(nodes)  # type: ignore pylance's wrong lint

    def sendFriendMessage(
        self,
        target: int,
        message: Message,
        quote: Optional[int] = None,
    ) -> FutureRet:
        data = {
            "target": target,
            "messageChain": self._formatMessage(message),
        }
        if quote: data['quote'] = quote
        return self.send("sendFriendMessage", None, data)

    def sendGroupMessage(
        self,
        target: int,
        message: Message,
        quote: Optional[int] = None,
    ) -> FutureRet:
        data = {
            "target": target,
            "messageChain": self._formatMessage(message),
        }
        if quote: data['quote'] = quote
        return self.send('sendGroupMessage', None, data)

    def sendTempMessage(
        self,
        target: int,
        group: int,
        message: Message,
        quote: Optional[int] = None,
    ) -> FutureRet:
        data = {
            "qq": target,
            "group": group,
            "messageChain": self._formatMessage(message),
        }
        if quote: data['quote'] = quote
        return self.send('sendTempMessage', None, data)

    def sendToAdmin(self, message: Message) -> FutureRet:
        if self.adminQid:
            return self.sendFriendMessage(
                target=self.adminQid,
                message=message,
            )
        else:
            raise ValueError('adminQid is not initialized')

    def reply(
        self,
        message: Message,
        quoteId: Optional[int] = None,
    ) -> FutureRet:
        ctx = contextStore.get(None)
        if ctx is None:
            raise RuntimeError("Unable to known reply target")
        sender = ctx.sender
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
            raise ValueError(f'Unsport Sender {sender.__class__.__name__}')

    def quoteReply(self, message: Message) -> FutureRet:
        messageId = contextStore.get().messageId
        logger.debug(f"quote reply to messageId={messageId}")
        return self.reply(message=message, quoteId=messageId)

    async def messageFromId(self, messageId: int) -> Optional[Context]:
        ret = await self.send("messageFromId", None, {"id": messageId})
        if ret['code'] == 0:
            return Context.parse_obj(ret['data'])
        else:
            logger.error(f"messageFromId failed: <{ret['code']}> {ret['msg']}")

    # TODO more method
