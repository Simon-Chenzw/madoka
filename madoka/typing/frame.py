from typing import TYPE_CHECKING, Awaitable, Callable, Optional

if TYPE_CHECKING:
    from ..bot import QQbot
    from .context import Context
    from .event import Event
    contextFunc = Callable[[QQbot, Context], Optional[Awaitable[None]]]
    contextCheckFunc = Callable[[QQbot, Context], bool]
    eventFunc = Callable[[QQbot, Event], Optional[Awaitable[None]]]
    timedFunc = Callable[[QQbot], Optional[Awaitable[None]]]
