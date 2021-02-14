from typing import TYPE_CHECKING, Awaitable, Callable, Optional, TypeVar

if TYPE_CHECKING:
    from ..bot import QQbot
    from .context import Context
    from .event import Event
    OptAwait = TypeVar('OptAwait', Awaitable[None], None)

    contextFunc = Callable[[QQbot, Context], Optional[Awaitable[None]]]
    contextFuncGen = Callable[[QQbot, Context], OptAwait]

    contextCheckFunc = Callable[[QQbot, Context], bool]

    eventFunc = Callable[[QQbot, Event], Optional[Awaitable[None]]]
    eventFuncGen = Callable[[QQbot, Event], OptAwait]

    timedFunc = Callable[[QQbot], Optional[Awaitable[None]]]
    timedFuncGen = Callable[[QQbot], OptAwait]
