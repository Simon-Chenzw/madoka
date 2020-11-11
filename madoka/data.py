from __future__ import absolute_import, annotations

import json
from typing import Any, Dict, Iterable, List, Literal, Optional, Union


class BaseOnJson:
    def __init__(self, json: Dict[str, Any]) -> None:
        self.json = json

    def __getitem__(self, key: str) -> Any:
        return self.json[key]


class Context(BaseOnJson):
    _sender: Optional[Sender] = None
    _messageChain: Optional[List['Text']] = None
    _text: Optional[str] = None

    def __init__(self, message: Union[str, Dict[str, Any]]) -> None:
        if isinstance(message, str):
            super().__init__(json.loads(message))
        else:
            super().__init__(message)

    @property
    def type(self) -> Literal['FriendMessage', 'GroupMessage', 'TempMessage']:
        return self['type']

    @property
    def sender(self) -> Sender:
        if self._sender is None:
            self._sender = SenderBase.trans(self.type, self['sender'])
        return self._sender

    @property
    def messageId(self) -> int:
        return self['messageChain'][0]['id']

    @property
    def messageChain(self) -> List['Text']:
        if self._messageChain is None:
            self._messageChain = [
                Text.trans(js) for js in self['messageChain']
            ]
        return self._messageChain

    def getFirst(self, type: str) -> Optional[Text]:
        for text in self.messageChain:
            if text.type == type:
                return text

    def getFirstImage(self) -> Optional[ImageText]:
        ret = self.getFirst("Image")
        return ret if isinstance(ret, ImageText) else None

    def getQuote(self) -> Optional[QuoteText]:
        ret = self.getFirst("Quote")
        return ret if isinstance(ret, QuoteText) else None

    def getAll(self, type: str) -> List[Text]:
        return [text for text in self.messageChain if text.type == type]

    def iter(self, type: str) -> Iterable[Text]:
        for text in self.messageChain:
            if text.type == type:
                yield text

    @property
    def text(self) -> str:
        if self._text is None:
            self._text = ''.join(text['text'] for text in self.iter("Plain"))
        return self._text


Sender = Union['FriendSender', 'GroupSender', 'TempSender']


class SenderBase(BaseOnJson):
    @property
    def id(self) -> int:
        return self['id']

    @staticmethod
    def trans(
        messsageType: Literal['FriendMessage', 'GroupMessage', 'TempMessage'],
        json: Dict[str, Any],
    ) -> Sender:
        if messsageType == 'FriendMessage':
            return FriendSender(json)
        elif messsageType == 'GroupMessage':
            return GroupSender(json)
        elif messsageType == 'TempMessage':
            return TempSender(json)
        else:
            raise ValueError(
                "sender's messsageType must be: 'FriendMessage', 'GroupMessage', 'TempMessage'"
            )


class FriendSender(SenderBase):
    @property
    def name(self) -> str:
        return self['nickname']

    @property
    def remark(self) -> str:
        return self['remark']


class GroupSender(SenderBase):
    @property
    def name(self) -> str:
        return self['memberName']

    @property
    def permission(self) -> Literal['OWNER', 'ADMINISTRATOR', 'MEMBER']:
        return self['permission']

    @property
    def groupId(self) -> int:
        return self['group']['id']

    @property
    def groupName(self) -> str:
        return self['group']['name']

    @property
    def selfPermission(self) -> Literal['OWNER', 'ADMINISTRATOR', 'MEMBER']:
        return self['group']['permission']


class TempSender(SenderBase):
    @property
    def name(self) -> str:
        return self['memberName']

    @property
    def permission(self) -> Literal['OWNER', 'ADMINISTRATOR', 'MEMBER']:
        return self['permission']

    @property
    def groupId(self) -> int:
        return self['group']['id']

    @property
    def groupName(self) -> str:
        return self['group']['name']

    @property
    def selfPermission(self) -> Literal['OWNER', 'ADMINISTRATOR', 'MEMBER']:
        return self['group']['permission']


class Text(BaseOnJson):
    @property
    def type(self) -> str:
        return self['type']

    @staticmethod
    def trans(json: Dict[str, Any]) -> Text:
        # TODO The way now is dirty
        type = json['type']
        if type == "Source":
            return SourceText(json)
        elif type == "Plain":
            return PlainText(json['text'])
        elif type == "Image":
            return ImageText(json['path'], json['url'])
        elif type == "Quote":
            return QuoteText(json)
        else:
            return Text(json)


class SourceText(Text):
    @property
    def id(self) -> int:
        return self['id']

    @property
    def time(self) -> int:
        return self['time']


class PlainText(Text):
    def __init__(self, text: str) -> None:
        super().__init__({
            "type": "Plain",
            "text": text,
        })

    @property
    def text(self) -> str:
        return self['text']


class ImageText(Text):
    def __init__(
        self,
        path: Optional[str] = None,
        url: Optional[str] = None,
    ) -> None:
        """
        :path: Need to be a relative path
        """
        super().__init__({
            "type": "Image",
            "path": path,
            "url": url,
        })

    @property
    def path(self) -> Optional[str]:
        return self['path']

    @property
    def url(self) -> Optional[str]:
        return self['url']


class QuoteText(Text):
    _text: Optional[str] = None

    @property
    def id(self) -> int:
        return self['id']

    @property
    def group(self) -> int:
        return self['groupId']

    @property
    def sender(self) -> int:
        return self['senderId']

    @property
    def target(self) -> int:
        return self['targetId']

    @property
    def origin(self) -> List[Text]:
        return self['origin']

    @property
    def text(self) -> str:
        if self._text is None:
            self._text = ''.join(text['text'] for text in self.origin
                                 if text['type'] == "Plain")
        return self._text

    @property
    def hasImage(self) -> bool:
        return '[图片]' in self.text


class Event(BaseOnJson):
    def __init__(self, message: Union[str, Any]) -> None:
        if isinstance(message, str):
            super().__init__(json.loads(message))
        else:
            super().__init__(message)

    @property
    def type(self) -> str:
        return self['type']


# TODO more Text and event
