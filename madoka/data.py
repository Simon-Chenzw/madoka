from __future__ import absolute_import, annotations

import json
from typing import Any, List, Literal, Optional, Union

MessageChain = List['Text']
Sender = Union['FriendSender', 'GroupSender', 'TempSender']


class Context:
    _sender: Optional[Sender] = None
    _text: Optional[List[Text]] = None

    def __init__(self, message: Union[str, Any]) -> None:
        if isinstance(message, str):
            self.js = json.loads(message)
        else:
            self.js = message

    def __getitem__(self, key: str) -> Any:
        return self.js[key]

    @property
    def type(self) -> Literal['FriendMessage', 'GroupMessage', 'TempMessage']:
        return self.js['type']

    @property
    def sender(self) -> Sender:
        if self._sender is None:
            if self.type == 'FriendMessage':
                self._sender = FriendSender(self.js['sender'])
            elif self.type == 'GroupMessage':
                self._sender = GroupSender(self.js['sender'])
            else:
                self._sender = TempSender(self.js['sender'])
        return self._sender

    @property
    def messageChain(self) -> MessageChain:
        if self._text is None:
            self._text = [Text(js) for js in self.js['messageChain']]
        return self._text

    @property
    def messageId(self) -> int:
        return self.js['messageChain'][0]['id']


class FriendSender:
    def __init__(self, js: Any) -> None:
        self.js = js

    def __getitem__(self, key: str) -> Any:
        return self.js[key]

    @property
    def id(self) -> int:
        return self.js['id']

    @property
    def name(self) -> str:
        return self.js['remark']


class GroupSender:
    def __init__(self, js: Any) -> None:
        self.js = js

    def __getitem__(self, key: str) -> Any:
        return self.js[key]

    @property
    def id(self) -> int:
        return self.js['id']

    @property
    def name(self) -> str:
        return self.js['memberName']

    @property
    def permission(self) -> Literal['OWNER', 'ADMINISTRATOR', 'MEMBER']:
        return self.js['permission']

    @property
    def groupId(self) -> int:
        return self.js['group']['id']

    @property
    def groupName(self) -> str:
        return self.js['group']['name']

    @property
    def selfPermission(self) -> Literal['OWNER', 'ADMINISTRATOR', 'MEMBER']:
        return self.js['group']['permission']


class TempSender:
    def __init__(self, js: Any) -> None:
        self.js = js

    def __getitem__(self, key: str) -> Any:
        return self.js[key]

    @property
    def id(self) -> int:
        return self.js['id']

    @property
    def name(self) -> str:
        return self.js['memberName']

    @property
    def permission(self) -> Literal['OWNER', 'ADMINISTRATOR', 'MEMBER']:
        return self.js['permission']

    @property
    def groupId(self) -> int:
        return self.js['group']['id']

    @property
    def groupName(self) -> str:
        return self.js['group']['name']

    @property
    def selfPermission(self) -> Literal['OWNER', 'ADMINISTRATOR', 'MEMBER']:
        return self.js['group']['permission']


class Text:
    def __init__(self, js: Any) -> None:
        self.js = js

    @property
    def type(self) -> str:
        return self.js['type']

    def __getitem__(self, key: str) -> Any:
        return self.js[key]


class PlainText(Text):
    def __init__(self, text: str) -> None:
        super().__init__({
            "type": "Plain",
            "text": text,
        })

    @property
    def text(self) -> str:
        return self.js['text']


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


class Event:
    def __init__(self, message: Union[str, Any]) -> None:
        if isinstance(message, str):
            self.js = json.loads(message)
        else:
            self.js = message

    def __getitem__(self, key: str) -> Any:
        return self.js[key]

    @property
    def type(self) -> str:
        return self.js['type']

# TODO more Text and event