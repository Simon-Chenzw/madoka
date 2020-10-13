from __future__ import absolute_import

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Callable, Optional, Tuple

from .base import BotBase

if TYPE_CHECKING:
    from .bot import QQbot

logger = logging.getLogger(__name__)


class TimeTask:
    def __init__(
        self,
        func: Callable[['QQbot'], None],
        start: datetime,
        interval: Optional[timedelta],
    ) -> None:
        self.func = func
        self.plan = start
        self.interval = interval
        if interval and interval.days < 0:
            raise ValueError("Interval should be positive")

    @property
    def timestamp(self) -> float:
        return self.plan.timestamp()

    def next(self) -> Optional['TimeTask']:
        if self.interval:
            self.plan = self.plan + self.interval
            return self
        else:
            return None

    @staticmethod
    def runOnce(func: Callable[['QQbot'], None], delay: int = 0) -> 'TimeTask':
        today = datetime.today()
        return TimeTask(
            func=func,
            start=today + timedelta(seconds=delay),
            interval=None,
        )

    @staticmethod
    def runRepeat(func: Callable[['QQbot'], None],
                  interval: int,
                  delay: int = 0) -> 'TimeTask':
        today = datetime.today()
        return TimeTask(
            func=func,
            start=today + timedelta(seconds=delay),
            interval=timedelta(seconds=interval),
        )

    @staticmethod
    def runEveryDay(func: Callable[['QQbot'], None],
                    hour: int = 0,
                    minute: int = 0,
                    second: int = 0) -> 'TimeTask':
        today = datetime.today()
        start = today.replace(
            hour=hour,
            minute=minute,
            second=second,
            microsecond=0,
        )
        while start < today:
            start = start + timedelta(days=1)
        return TimeTask(
            func=func,
            start=start,
            interval=timedelta(days=1),
        )

    @staticmethod
    def runEveryWeek(func: Callable[['QQbot'], None],
                     weekday: int = 0,
                     hour: int = 0,
                     minute: int = 0,
                     second: int = 0) -> 'TimeTask':
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
        while start < today:
            start = start + timedelta(days=1)
        while start.weekday() != weekday:
            start = start + timedelta(days=1)
        return TimeTask(func=func, start=start, interval=timedelta(days=7))


class ScheduleUnit(BotBase):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def __enter__(self) -> 'ScheduleUnit':
        super().__enter__()
        self._timeQueue: 'asyncio.PriorityQueue[Tuple[float,TimeTask]]' = asyncio.PriorityQueue(
            loop=self.loop)
        return self

    def addTimeTask(self, task: TimeTask):
        logger.debug(f"add timeTask: {task.func.__name__}")
        self._timeQueue.put_nowait((task.timestamp, task))

    async def _schedule(self, bot: 'QQbot') -> None:
        logger.info(f"schedule online")
        while True:
            # TODO: low performance.
            timestamp, task = await self._timeQueue.get()
            if timestamp <= time.time():
                # TODO: low performance. should use 'run_in_executor'
                logger.info(f"TimeTask: {task.func.__name__}")
                try:
                    task.func(bot)
                except Exception as err:
                    logger.exception(f"schedule module: {task.func.__name__}")
                if task.interval:
                    task.next()
                    self._timeQueue.put_nowait((task.timestamp, task))
            else:
                self._timeQueue.put_nowait((timestamp, task))
                await asyncio.sleep(1)
            self._timeQueue.task_done()

    # special timetask method is below

    def runOnce(
        self,
        func: Callable[['QQbot'], None],
        delay: int = 0,
    ) -> None:
        self.addTimeTask(TimeTask.runOnce(
            func=func,
            delay=delay,
        ))

    def runRepeat(
        self,
        func: Callable[['QQbot'], None],
        interval: int,
        delay: int = 0,
    ) -> None:
        self.addTimeTask(
            TimeTask.runRepeat(
                func=func,
                interval=interval,
                delay=delay,
            ))

    def runEveryDay(
        self,
        func: Callable[['QQbot'], None],
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
    ) -> None:
        self.addTimeTask(
            TimeTask.runEveryDay(
                func=func,
                hour=hour,
                minute=minute,
                second=second,
            ))

    def runEveryWeek(
        self,
        func: Callable[['QQbot'], None],
        weekday: int = 0,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
    ) -> None:
        """
        :weekday: 0 means Monday, 6 means Sunday
        """
        self.addTimeTask(
            TimeTask.runEveryWeek(
                func=func,
                weekday=weekday,
                hour=hour,
                minute=minute,
                second=second,
            ))
