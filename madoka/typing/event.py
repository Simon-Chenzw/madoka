from __future__ import annotations

from typing import Literal, Type, get_args, get_origin

from pydantic import BaseModel  # pylint: disable=no-name-in-module


class Event(BaseModel, extra='forbid'):
    """
    auto choice subclass when instantiating
    __init__ of subclass should be compatible with pydantic
    :type: Used for type checking, but Event should not be instantiated
    """

    type: str

    class TypeMap:
        types: dict[str, Type[Event]] = {}
        extra: Type[Event]

        @classmethod
        def add(cls, name: str, cls_: Type[Event]) -> None:
            if name not in cls.types:
                cls.types[name] = cls_
            else:
                raise ValueError("type can't have same typename")

        @classmethod
        def get(cls, name: str) -> Type[Event]:
            return cls.types.get(name, cls.extra)

    def __init_subclass__(cls: Type[Event], **kwargs) -> None:
        if 'type' in cls.__fields__ and get_origin(
                cls.__fields__['type'].type_) is Literal:
            cls.TypeMap.add(
                get_args(cls.__fields__['type'].type_)[0],
                cls,
            )
        elif cls.__name__ == 'ExtraEvent':
            cls.TypeMap.extra = cls
        return super().__init_subclass__(**kwargs)

    def __new__(cls, *args, **kwargs) -> Type[Event]:
        if cls is Event:
            if 'type' in kwargs:
                return super().__new__(cls.TypeMap.get(kwargs['type']))
            else:
                return super().__new__(cls.TypeMap.extra)
        else:
            return super().__new__(cls)


class ExtraEvent(Event, extra='allow'):
    pass


class BotOnlineEvent(Event):
    type: Literal['BotOnlineEvent']
    qq: int


class BotOfflineEventActive(Event):
    type: Literal['BotOfflineEventActive']
    qq: int


class BotOfflineEventForce(Event):
    type: Literal['BotOfflineEventForce']
    qq: int


class BotOfflineEventDropped(Event):
    type: Literal['BotOfflineEventDropped']
    qq: int


class BotReloginEvent(Event):
    type: Literal['BotReloginEvent']
    qq: int


# TODO more Event and resp
