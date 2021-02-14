from __future__ import annotations

import asyncio
import logging
import time
from typing import TYPE_CHECKING, Optional, Tuple, Union

from ..register import Schedule
from .base import BotBase

if TYPE_CHECKING:
    from ..typing.frame import timedFunc

logger = logging.getLogger('madoka')


class TimedTask(Schedule):
    def __init__(self, func: timedFunc, schedule: Schedule) -> None:
        super().__init__(schedule.plan, schedule.interval)
        self.func = func

    def next(self) -> Optional[TimedTask]:
        if self.interval:
            return TimedTask(
                func=self.func,
                schedule=Schedule(
                    start=self.plan + self.interval,
                    interval=self.interval,
                ),
            )
        else:
            return None


class ScheduleUnit(BotBase):
    def __enter__(self) -> ScheduleUnit:
        super().__enter__()
        self._timeQueue: 'asyncio.PriorityQueue[TimedTask]' = asyncio.PriorityQueue(
            loop=self._loop)
        return self

    def addTimedTask(
        self,
        func: timedFunc,
        timeSetting: Union[int, Tuple[int, int], Schedule],
    ) -> None:
        if isinstance(timeSetting, int):
            schedule = Schedule.runOnce(timeSetting)
        elif isinstance(timeSetting, tuple):
            schedule = Schedule.runRepeat(timeSetting[0], timeSetting[1])
        else:
            schedule = timeSetting
        logger.debug(f"add TimedTask: {func.__name__} {schedule.timestamp}")
        self._timeQueue.put_nowait(TimedTask(func, schedule))

    async def _schedule(self) -> None:
        async def solve(task: TimedTask) -> None:
            try:
                ret = task.func(self._bot)
                if ret and asyncio.iscoroutine(ret):
                    await ret
            except:
                logger.exception(f"schedule module: {task.func.__name__}")

        logger.info(f"schedule online")
        while True:
            task = await self._timeQueue.get()
            if task.timestamp <= time.time():
                logger.info(f"TimedTask: {task.func.__name__}")
                self.create_task(solve(task))
                next_task = task.next()
                if next_task:
                    self._timeQueue.put_nowait(next_task)
                self._timeQueue.task_done()
            else:
                self._timeQueue.put_nowait(task)
                self._timeQueue.task_done()
                await asyncio.sleep(1)
