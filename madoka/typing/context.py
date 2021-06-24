from __future__ import annotations

from typing import Iterator, Literal, Optional, Type, TypeVar, get_args, get_origin

from pydantic import BaseModel  # pylint: disable=no-name-in-module

from .sender import (FriendSender, GroupSender, OtherClientSender, Sender,
                     StrangerSender, TempSender)
from .text import SourceText, Text

T_Text = TypeVar('T_Text', bound=Text)


class Context(BaseModel, extra='forbid'):
    """
    auto choice subclass when instantiating
    all instantiate should use pydantic
    :params: Used for type checking, but Text should not be instantiated
    """

    type: str
    messageChain: list[Text]
    sender: Sender

    class TypeMap:
        type_key: str = 'type'
        types: dict[str, Type[Context]] = {}

        @classmethod
        def add(cls, ins_cls: Type[Context]) -> None:
            field = ins_cls.__fields__.get(cls.type_key)
            if field is None: return
            if get_origin(field.type_) is Literal:
                for name in get_args(field.type_):
                    assert name not in cls.types, "can't have same key value"
                    cls.types[name] = ins_cls

    def __init_subclass__(cls, **kwargs) -> None:
        cls.TypeMap.add(cls)
        return super().__init_subclass__()

    def __new__(cls, *args, **kwargs) -> Type[Context]:
        key = cls.TypeMap.type_key
        if cls is Context:
            if key in kwargs:
                new_cls = cls.TypeMap.types.get(kwargs[key], Context)
                return super().__new__(new_cls)  # type: ignore
            else:
                return super().__new__(Context)
        else:
            return super().__new__(cls)

    @property
    def messageId(self) -> int:
        return self.getExist(SourceText).id

    @property
    def text(self) -> str:
        # TODO lazy load
        return ''.join(map(str, self.messageChain))

    def get(self, type: Type[T_Text]) -> Optional[T_Text]:
        """
        :return: return the first one, or None
        """
        try:
            return next(self.iter(type))
        except:
            return None

    def getExist(self, type: Type[T_Text]) -> T_Text:
        """
        if not exist, raise AssertionError
        :return: return the first one
        """
        ret = self.get(type)
        assert ret is not None, f"{type.__name__} don't exist"
        return ret

    def iter(self, type: Type[T_Text]) -> Iterator[T_Text]:
        for text in self.messageChain:
            if isinstance(text, type):
                yield text

    def getAll(self, type: Type[T_Text]) -> list[T_Text]:
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


class StrangerContext(Context):
    type: Literal['StrangerMessage']
    sender: StrangerSender


class OtherClientContext(Context):
    type: Literal['OtherClientMessage']
    sender: OtherClientSender
