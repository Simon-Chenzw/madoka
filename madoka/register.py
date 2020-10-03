from __future__ import absolute_import, annotations

import logging
from typing import TYPE_CHECKING, Callable, List

from .schedule import TimeTask
from .data import Context

if TYPE_CHECKING:
    from .bot import QQbot

registered: List[Callable[[QQbot, Context], None]] = []
scheduleRegistered: List[TimeTask] = []

logger = logging.getLogger(__name__)


def getRegister() -> List[Callable[[QQbot, Context], None]]:
    return registered


def getScheduleRegistered() -> List[TimeTask]:
    return scheduleRegistered


def register(
    func: Callable[[QQbot, Context],
                   None]) -> Callable[[QQbot, Context], None]:
    registered.append(func)
    return func


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
