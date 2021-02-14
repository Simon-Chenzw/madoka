from __future__ import annotations

from typing import TYPE_CHECKING, Callable, List, Tuple

if TYPE_CHECKING:
    from ..typing.frame import OptAwait, eventFunc, eventFuncGen

registered: List[Tuple[str, eventFunc]] = []


def getRegistered() -> List[Tuple[str, eventFunc]]:
    return registered


def register(
        type: str
) -> Callable[[eventFuncGen[OptAwait]], eventFuncGen[OptAwait]]:
    def inner(func: eventFuncGen[OptAwait]) -> eventFuncGen[OptAwait]:
        registered.append((type, func))
        return func

    return inner
