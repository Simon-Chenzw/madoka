from __future__ import annotations

import asyncio
import inspect
import logging
import time
from datetime import datetime
from itertools import count, repeat
from typing import (TYPE_CHECKING, Any, Awaitable, Callable, Iterator, TypeVar,
                    Union)

from croniter.croniter import croniter

from .base import BotBase

if TYPE_CHECKING:
    from .bot import QQbot

    timed = Union[int, float, datetime]

    Ret = Union[None, Awaitable[None]]
    OptAwait = TypeVar('OptAwait', None, Awaitable[None])
    timedFunc = Callable[[QQbot], Ret]
    timedFuncGen = Callable[[QQbot], OptAwait]
    timedFuncWrap = Callable[[timedFuncGen], timedFuncGen]

logger = logging.getLogger(__name__)


class Task:
    def __init__(
        self,
        func: timedFunc,
        iter: Iterator[timed],
    ) -> None:
        self.func = func
        self.iter = iter
        nxt = next(self.iter)
        if isinstance(nxt, datetime):
            self.time: datetime = nxt
        else:
            self.time: datetime = datetime.fromtimestamp(nxt)

    def next(self) -> Task:
        nxt = next(self.iter)
        if isinstance(nxt, datetime):
            self.time: datetime = nxt
        else:
            self.time: datetime = datetime.fromtimestamp(nxt)
        return self

    @property
    def timestamp(self) -> float:
        return self.time.timestamp()

    def __lt__(self, o: Task) -> bool:
        return self.time < o.time

    def __le__(self, o: Task) -> bool:
        return self.time <= o.time

    def __eq__(self, o: Task) -> bool:
        return self.time == o.time

    def __ne__(self, o: Task) -> bool:
        return self.time != o.time

    def __ge__(self, o: Task) -> bool:
        return self.time >= o.time

    def __gt__(self, o: Task) -> bool:
        return self.time > o.time


class ScheduleUnit(BotBase):
    _timedLst: list[Task]
    _timeQueue: asyncio.PriorityQueue[Task]

    def __new__(cls, *args, **kwargs) -> Any:
        obj = super().__new__(cls)
        obj._timedLst = []
        return obj

    async def __aenter__(self) -> ScheduleUnit:
        await super().__aenter__()
        self._timeQueue = asyncio.PriorityQueue()
        for task in self._timedLst:
            self._timeQueue.put_nowait(task)
        return self

    def runOnce(self, delay: int = 0) -> timedFuncWrap:
        return self.addTimed(repeat(time.time() + delay, 1))

    def runRepect(self, interval: int = 0, delay: int = 0) -> timedFuncWrap:
        return self.addTimed(count(time.time() + delay, interval))

    def runCron(self, cron: str) -> timedFuncWrap:
        return self.addTimed(
            croniter(
                cron,
                start_time=datetime.today(),
                ret_type=datetime,
            ))

    def addTimed(self, it: Iterator[timed]) -> timedFuncWrap:
        """
        :it: iter of Task datetime or timestamp
        """
        def wrapper(func: timedFuncGen) -> timedFuncGen:
            task = Task(func, it)
            logger.debug(f"add Task: {task.func.__name__} {task.time}")
            self._timedLst.append(task)
            if hasattr(self, "_timeQueue"):
                self._timeQueue.put_nowait(task)
            return func

        return wrapper

    async def _schedule(self) -> None:
        async def solve(task: Task) -> None:
            try:
                ret = task.func(self._bot)
                if inspect.isawaitable(ret): await ret
            except:
                logger.exception(f"schedule module: {task.func.__name__}")

        logger.debug(f"Start schedule")
        while True:
            task = await self._timeQueue.get()
            if task.timestamp <= time.time():
                logger.info(f"Task run: {task.func.__name__}")
                asyncio.create_task(solve(task))
                try:
                    self._timeQueue.put_nowait(task.next())
                except StopIteration:
                    logger.debug(f"Task end: {task.func.__name__}")
            else:
                self._timeQueue.put_nowait(task)
                await asyncio.sleep(1)
            self._timeQueue.task_done()
