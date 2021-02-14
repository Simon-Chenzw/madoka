from __future__ import annotations

from typing import TYPE_CHECKING, Callable, List, Tuple

if TYPE_CHECKING:
    from ..typing.frame import eventFunc

registered: List[Tuple[str, eventFunc]] = []


def getRegistered() -> List[Tuple[str, eventFunc]]:
    return registered


def register(type: str) -> Callable[[eventFunc], eventFunc]:
    def inner(func: eventFunc) -> eventFunc:
        registered.append((type, func))
        return func

    return inner
