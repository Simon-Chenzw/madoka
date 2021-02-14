from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING, Callable, List, Optional

if TYPE_CHECKING:
    from ..bot import QQbot
    from ..typing import Context
    from ..typing.frame import contextCheckFunc, contextFunc

# TODO mark registered function's origin module
registered: List[contextFunc] = []


# TODO condition
def getRegistered() -> List[contextFunc]:
    return registered


def register(
    check: Optional[contextCheckFunc] = None,
) -> Callable[[contextFunc], contextFunc]:
    def wrapper(func: contextFunc) -> contextFunc:
        @wraps(func)
        def inner(bot: 'QQbot', context: Context):
            if check(bot, context):
                return func(bot, context)

        if check:
            registered.append(inner)
        else:
            registered.append(func)
        return func

    return wrapper