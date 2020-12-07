from __future__ import absolute_import, annotations, generator_stop

import logging
from functools import wraps
from typing import TYPE_CHECKING, Awaitable, Callable, List, Optional, Tuple

from .data import Context, Event
from .schedule import TimeTask

if TYPE_CHECKING:
    from .bot import QQbot
    contextFunction = Callable[[QQbot, Context], Optional[Awaitable[None]]]
    eventFunction = Callable[[QQbot, Event], Optional[Awaitable[None]]]
    TimeTaskFunction = Callable[[QQbot], Optional[Awaitable[None]]]

registered: List[contextFunction] = []
eventRegistered: List[Tuple[str, eventFunction]] = []
scheduleRegistered: List[TimeTask] = []

logger = logging.getLogger(__name__)


def getRegister() -> List[contextFunction]:
    return registered


def getEventRegistered() -> List[Tuple[str, eventFunction]]:
    return eventRegistered


def getScheduleRegistered() -> List[TimeTask]:
    return scheduleRegistered


def register(check: Callable[[Context], bool]):
    def inner(func: contextFunction) -> contextFunction:
        @wraps(func)
        def wrapper(bot: 'QQbot', context: Context):
            if check(context):
                return func(bot, context)

        registered.append(wrapper)
        return func

    return inner


def eventRegister(type: str):
    def inner(func: eventFunction) -> eventFunction:
        eventRegistered.append((type, func))
        return func

    return inner


def runOnce(delay: int = 0) -> Callable[[TimeTaskFunction], TimeTaskFunction]:
    def register(func: TimeTaskFunction) -> TimeTaskFunction:
        scheduleRegistered.append(TimeTask.runOnce(
            func=func,
            delay=delay,
        ))
        return func

    return register


def runRepeat(
    interval: int,
    delay: int = 0,
) -> Callable[[TimeTaskFunction], TimeTaskFunction]:
    def register(func: TimeTaskFunction) -> TimeTaskFunction:
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
) -> Callable[[TimeTaskFunction], TimeTaskFunction]:
    def register(func: TimeTaskFunction) -> TimeTaskFunction:
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
) -> Callable[[TimeTaskFunction], TimeTaskFunction]:
    """
    :weekday: 0 means Monday, 6 means Sunday
    """
    def register(func: TimeTaskFunction) -> TimeTaskFunction:
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
