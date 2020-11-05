from __future__ import absolute_import, annotations

import logging
from typing import TYPE_CHECKING, Callable, List, Tuple

from .data import Context, Event
from .filter import Censor, auth
from .schedule import TimeTask

if TYPE_CHECKING:
    from .bot import QQbot

registered: List[Callable[[QQbot, Context], None]] = []
eventRegistered: List[Tuple[str, Callable[[QQbot, Event], None]]] = []
scheduleRegistered: List[TimeTask] = []

logger = logging.getLogger(__name__)


def getRegister() -> List[Callable[[QQbot, Context], None]]:
    return registered


def getEventRegistered() -> List[Tuple[str, Callable[[QQbot, Event], None]]]:
    return eventRegistered


def getScheduleRegistered() -> List[TimeTask]:
    return scheduleRegistered


def register(censor: Censor):
    def inner(
        func: Callable[[QQbot, Context], None],
    ) -> Callable[[QQbot, Context], None]:
        registered.append(auth(censor)(func))
        return func

    return inner


def eventRegister(type: str):
    def inner(
        func: Callable[[QQbot, Event],
                       None], ) -> Callable[[QQbot, Event], None]:
        eventRegistered.append((type, func))
        return func

    return inner


def runOnce(
    delay: int = 0,
) -> Callable[[Callable[[QQbot], None]], Callable[[QQbot], None]]:
    def register(func: Callable[[QQbot], None]) -> Callable[[QQbot], None]:
        scheduleRegistered.append(TimeTask.runOnce(
            func=func,
            delay=delay,
        ))
        return func

    return register


def runRepeat(
    interval: int,
    delay: int = 0,
) -> Callable[[Callable[[QQbot], None]], Callable[[QQbot], None]]:
    def register(func: Callable[[QQbot], None]) -> Callable[[QQbot], None]:
        scheduleRegistered.append(
            TimeTask.runRepeat(
                func=func,
                interval=interval,
                delay=delay,
            ))
        return func

    return register


def runEveryDay(
    hour: int = 0,
    minute: int = 0,
    second: int = 0,
) -> Callable[[Callable[[QQbot], None]], Callable[[QQbot], None]]:
    def register(func: Callable[[QQbot], None]) -> Callable[[QQbot], None]:
        scheduleRegistered.append(
            TimeTask.runEveryDay(
                func=func,
                hour=hour,
                minute=minute,
                second=second,
            ))
        return func

    return register


def runEveryWeek(
    weekday: int = 0,
    hour: int = 0,
    minute: int = 0,
    second: int = 0,
) -> Callable[[Callable[[QQbot], None]], Callable[[QQbot], None]]:
    """
    :weekday: 0 means Monday, 6 means Sunday
    """
    def register(func: Callable[[QQbot], None]) -> Callable[[QQbot], None]:
        scheduleRegistered.append(
            TimeTask.runEveryWeek(
                func=func,
                weekday=weekday,
                hour=hour,
                minute=minute,
                second=second,
            ))
        return func

    return register
