from __future__ import annotations

import json
from typing import (Any, Dict, Iterator, List, Literal, Optional, Type,
                    TypeVar, Union)

from .sender import Sender, SenderBase
from .text import SourceText, Text

T = TypeVar('T')


class Context:
    _sender: Optional[Sender] = None
    _messageChain: Optional[List[Text]] = None
    _text: Optional[str] = None

    def __init__(self, message: Union[str, Dict[str, Any]]) -> None:
        if isinstance(message, str):
            self._json = json.loads(message)
        else:
            self._json = message

    def __getitem__(self, key: str) -> Any:
        return self._json[key]

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
        return self.getExist(SourceText).id

    @property
    def messageChain(self) -> List[Text]:
        if self._messageChain is None:
            self._messageChain = [
                Text.trans(js) for js in self['messageChain']
            ]
        return self._messageChain

    @property
    def text(self) -> str:
        if self._text is None:
            self._text = ''.join(map(str, self.messageChain))
        return self._text

    def get(self, type: Type[T]) -> Optional[T]:
        """
        :return: return the first one, or None
        """
        try:
            return next(self.iter(type))
        except:
            return None

    def getExist(self, type: Type[T]) -> T:
        """
        if not exist, raise AssertionError
        :return: return the first one
        """
        ret = self.get(type)
        assert ret is not None, f"{type.__name__} don't exist"
        return ret

    def iter(self, type: Type[T]) -> Iterator[T]:
        for text in self.messageChain:
            if isinstance(text, type):
                yield text  # type 'Never'?

    def getAll(self, type: Type[T]) -> List[T]:
        return list(self.iter(type))
