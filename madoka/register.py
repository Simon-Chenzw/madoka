from __future__ import absolute_import, annotations, generator_stop

import logging
from functools import wraps
from typing import TYPE_CHECKING, Callable, Coroutine, List, Optional, Tuple

from .data import Context, Event
from .schedule import TimeTask

if TYPE_CHECKING: 
    from .bot import QQbot
    # TODO add Coroutine in function
    # TODO change type hinting into data.py (maybe)
    # functionReturn = Optional[Coroutine[None, None, None]]
    contentChecker = Callable[[Context], bool]
    contextFunction = Callable[[QQbot, Context], None]
    eventFunction = Callable[[QQbot, Event], None]
    eventTuple = Tuple[str, eventFunction]
    TimeTaskFunction = Callable[[QQbot], None]
    TimeTaskRegister = Callable[[TimeTaskFunction], TimeTaskFunction]

registered: List[contextFunction] = []
eventRegistered: List[eventTuple] = []
scheduleRegistered: List[TimeTask] = []

logger = logging.getLogger(__name__)


def getRegister() -> List[contextFunction]:
    return registered


def getEventRegistered() -> List[eventTuple]:
    return eventRegistered


def getScheduleRegistered() -> List[TimeTask]:
    return scheduleRegistered


def register(check: contentChecker):
    def inner(func: contextFunction) -> contextFunction:
        @wraps(func)
        def wrapper(bot: 'QQbot', context: Context):
            if check(context):
                func(bot, context)

        registered.append(wrapper)
        return func

    return inner


def eventRegister(type: str):
    def inner(func: eventFunction) -> eventFunction:
        eventRegistered.append((type, func))
        return func

    return inner


def runOnce(delay: int = 0) -> TimeTaskRegister:
    def register(func: TimeTaskFunction) -> TimeTaskFunction:
        scheduleRegistered.append(TimeTask.runOnce(
            func=func,
            delay=delay,
        ))
        return func

    return register


def runRepeat(interval: int, delay: int = 0) -> TimeTaskRegister:
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
) -> TimeTaskRegister:
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
) -> TimeTaskRegister:
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
