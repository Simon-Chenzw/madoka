from __future__ import annotations

import asyncio
import inspect
import logging
from contextvars import ContextVar
from typing import (TYPE_CHECKING, Any, Awaitable, Callable, Optional, Type,
                    TypeVar, Union)

from ..typing import Context, Event
from .base import BotBase

if TYPE_CHECKING:
    from .bot import QQbot

    Ret = Union[None, Awaitable[None]]
    OptAwait = TypeVar('OptAwait', None, Awaitable[None])

    ctxCensor = Callable[[QQbot, Context], bool]
    ctxFunc = Callable[[QQbot, Context], Ret]
    ctxFuncGen = Callable[[QQbot, Context], OptAwait]
    ctxFuncWrap = Callable[[ctxFuncGen], ctxFuncGen]

    eventFunc = Callable[[QQbot, Event], Ret]
    eventFuncGen = Callable[[QQbot, Event], OptAwait]
    eventFuncWrap = Callable[[eventFuncGen], eventFuncGen]

logger = logging.getLogger(__name__)

contextStore: ContextVar[Context] = ContextVar('context')


class SolveUnit(BotBase):
    _ctxLst: list[ctxFunc]
    _eventLst: dict[Type[Event], list[eventFunc]]

    def __new__(cls, *args, **kwargs) -> Any:
        obj = super().__new__(cls)
        obj._ctxLst = []
        obj._eventLst = {}
        return obj

    def addFunction(self, check: Optional[ctxCensor] = None) -> ctxFuncWrap:
        def wrapper(func: ctxFuncGen) -> ctxFuncGen:
            def inner(bot: QQbot, context: Context) -> Ret:
                if check(bot, context):
                    return func(bot, context)

            self._ctxLst.append(inner)
            return func

        return wrapper

    def addEvent(self, event: Type[Event]) -> eventFuncWrap:
        def wrapper(func: eventFuncGen) -> eventFuncGen:
            self._eventLst.setdefault(event, []).append(func)
            return func

        return wrapper

    async def _solve(self):
        logger.info("Start solving")
        async for data in self._recv():
            if data['type'][-7:] == "Message":
                asyncio.create_task(self._solveCtx(data))
            else:
                asyncio.create_task(self._solveEvent(data))

    async def _solveCtx(self, data: dict[str, Any]) -> None:
        async def solve(func: ctxFunc) -> None:
            try:
                logger.debug(f"Context solve: func={func.__name__}\n {ctx=}")
                ret = func(self._bot, ctx)
                if inspect.isawaitable(ret): await ret
            except:
                logger.exception(f"Context: func={func.__name__}\n {ctx=}")

        ctx = Context.parse_obj(data)
        contextStore.set(ctx)
        for func in self._ctxLst:
            asyncio.create_task(solve(func))

    async def _solveEvent(self, data: dict[str, Any]) -> None:
        async def solve(func: eventFunc) -> None:
            try:
                logger.debug(f"Event solve: func={func.__name__}\n {event=}")
                ret = func(self._bot, event)
                if inspect.isawaitable(ret): await ret
            except:
                logger.exception(f"Event: func={func.__name__}\n {event=}")

        event = Event.parse_obj(data)
        for k, v in self._eventLst.items():
            if isinstance(event, k):
                for func in v:
                    asyncio.create_task(solve(func))
