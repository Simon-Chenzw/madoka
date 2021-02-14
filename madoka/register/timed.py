from __future__ import annotations
from typing import TYPE_CHECKING, Awaitable, Callable, List, Optional, Tuple

if TYPE_CHECKING:
    from ..bot import QQbot
    from .schedule import Schedule
    from ..typing.frame import timedFunc

registered: List[Tuple[timedFunc, Schedule]] = []


def getRegistered() -> List[Tuple[timedFunc, Schedule]]:
    return registered


def register(schedule: Schedule) -> Callable[[timedFunc], timedFunc]:
    def inner(func: timedFunc) -> timedFunc:
        registered.append((func, schedule))
        return func

    return inner
