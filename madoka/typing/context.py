from __future__ import annotations

from typing import Iterator, List, Literal, Optional, Type, TypeVar

from pydantic import BaseModel  # pylint: disable=no-name-in-module

from .sender import FriendSender, GroupSender, Sender, TempSender
from .text import SourceText, Text

G_Text = TypeVar('G_Text', bound=Text)


class Context(BaseModel, extra='forbid'):
    """
    auto choice subclass when instantiating
    all instantiate should use pydantic
    :params: Used for type checking, but Text should not be instantiated
    """

    type: Literal['FriendMessage', 'GroupMessage', 'TempMessage']
    messageChain: List[Text]
    sender: Sender

    def __new__(cls, *args, **kwargs) -> Type[Context]:
        if cls is Context:
            if kwargs['type'] == 'FriendMessage':
                return super().__new__(FriendContext)
            elif kwargs['type'] == 'GroupMessage':
                return super().__new__(GroupContext)
            elif kwargs['type'] == 'TempMessage':
                return super().__new__(TempContext)
            else:
                raise ValueError("Error Context type")
        else:
            return super().__new__(cls)

    @property
    def messageId(self) -> int:
        return self.getExist(SourceText).id

    @property
    def text(self) -> str:
        # TODO lazy load
        return ''.join(map(str, self.messageChain))

    def get(self, type: Type[G_Text]) -> Optional[G_Text]:
        """
        :return: return the first one, or None
        """
        try:
            return next(self.iter(type))
        except:
            return None

    def getExist(self, type: Type[G_Text]) -> G_Text:
        """
        if not exist, raise AssertionError
        :return: return the first one
        """
        ret = self.get(type)
        assert ret is not None, f"{type.__name__} don't exist"
        return ret

    def iter(self, type: Type[G_Text]) -> Iterator[G_Text]:
        for text in self.messageChain:
            if isinstance(text, type):
                yield text

    def getAll(self, type: Type[G_Text]) -> List[G_Text]:
        return list(self.iter(type))


class FriendContext(Context):
    type: Literal['FriendMessage']
    sender: FriendSender


class GroupContext(Context):
    type: Literal['GroupMessage']
    sender: GroupSender


class TempContext(Context):
    type: Literal['TempMessage']
    sender: TempSender
