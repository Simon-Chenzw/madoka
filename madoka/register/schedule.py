from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional


class Schedule:
    def __init__(self, start: datetime, interval: Optional[timedelta]) -> None:
        # TODO start can be None, represent the time bot start
        self.plan = start
        self.interval = interval
        if interval and interval.days < 0:
            raise ValueError("Interval should be positive")

    @property
    def timestamp(self) -> float:
        return self.plan.timestamp()

    def next(self) -> Optional[Schedule]:
        if self.interval:
            return Schedule(
                start=self.plan + self.interval,
                interval=self.interval,
            )
        else:
            return None

    def __lt__(self, rhs) -> bool:
        return self.timestamp < rhs.timestamp

    def __gt__(self, rhs) -> bool:
        return self.timestamp > rhs.timestamp

    def __le__(self, rhs) -> bool:
        return self.timestamp <= rhs.timestamp

    def __ge__(self, rhs) -> bool:
        return self.timestamp >= rhs.timestamp

    def __eq__(self, rhs) -> bool:
        return self.timestamp == rhs.timestamp

    def __ne__(self, rhs) -> bool:
        return self.timestamp != rhs.timestamp

   
def runOnce(delay: int = 0) -> Schedule:
    return Schedule(
        start=datetime.today() + timedelta(seconds=delay),
        interval=None,
    )


def runRepeat(interval: int, delay: int = 0) -> Schedule:
    return Schedule(
        start=datetime.today() + timedelta(seconds=delay),
        interval=timedelta(seconds=interval),
    )


def runEveryDay(
    hour: int = 0,
    minute: int = 0,
    second: int = 0,
) -> Schedule:
    today = datetime.today()
    start = today.replace(
        hour=hour,
        minute=minute,
        second=second,
        microsecond=0,
    )
    while start < today:
        start += timedelta(days=1)
    return Schedule(
        start=start,
        interval=timedelta(days=1),
    )


def runEveryWeek(
    weekday: int = 0,
    hour: int = 0,
    minute: int = 0,
    second: int = 0,
) -> Schedule:
    """
    :weekday: 0 means Monday, 6 means Sunday
    """
    today = datetime.today()
    start = today.replace(
        hour=hour,
        minute=minute,
        second=second,
        microsecond=0,
    )
    while start < today or start.weekday() != weekday:
        start += timedelta(days=1)
    return Schedule(
        start=start,
        interval=timedelta(days=7),
    )
