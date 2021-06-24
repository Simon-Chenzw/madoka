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
        type_key: str = 'type'
        types: dict[str, Type[Event]] = {}
        extra_name: str = 'ExtraEvent'
        extra: Type[Event]

        @classmethod
        def add(cls, ins_cls: Type[Event]) -> None:
            if ins_cls.__name__ == cls.extra_name:
                cls.extra = ins_cls
                return

            field = ins_cls.__fields__.get(cls.type_key)
            if field is None:
                return

            if get_origin(field.type_) is Literal:
                for name in get_args(field.type_):
                    assert name not in cls.types, "can't have same key value"
                    cls.types[name] = ins_cls

    def __init_subclass__(cls, **kwargs) -> None:
        cls.TypeMap.add(cls)
        return super().__init_subclass__()

    def __new__(cls, *args, **kwargs) -> Type[Event]:
        key = cls.TypeMap.type_key
        if cls is Event:
            if key in kwargs:
                new_cls = cls.TypeMap.types.get(kwargs[key], cls.TypeMap.extra)
                return super().__new__(new_cls)
            else:
                return super().__new__(cls.TypeMap.extra)  # type: ignore
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
