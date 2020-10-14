from __future__ import absolute_import, annotations

from functools import wraps
from typing import TYPE_CHECKING, Callable, List, Union

from .data import Context, FriendSender, GroupSender, TempSender

if TYPE_CHECKING:
    from .bot import QQbot


class Censor:
    check: Callable[[Context], bool] = lambda js: True

    def __init__(
        self,
        check_func: Callable[[Context], bool],
    ) -> None:
        self.check = check_func

    def __eq__(self, rhs: Censor) -> Censor:
        return Censor(lambda js: self.check(js) == rhs.check(js))

    def __nq__(self, rhs: Censor) -> Censor:
        return Censor(lambda js: self.check(js) != rhs.check(js))

    def __and__(self, rhs: Censor) -> Censor:
        return Censor(lambda js: self.check(js) and rhs.check(js))

    def __or__(self, rhs: Censor) -> Censor:
        return Censor(lambda js: self.check(js) or rhs.check(js))

    def __invert__(self) -> Censor:
        return Censor(lambda js: not self.check(js))


def auth(filter: Censor):
    def wrapper(
        func: Callable[['QQbot', Context], None]
    ) -> Callable[['QQbot', Context], None]:
        @wraps(func)
        def inner(bot: 'QQbot', context: Context):
            if filter.check(context):
                func(bot, context)

        return inner

    return wrapper


isFriendMessage = Censor(
    lambda context: isinstance(context.sender, FriendSender), )
isGroupMessage = Censor(
    lambda context: isinstance(context.sender, GroupSender), )
isTempMessage = Censor(
    lambda context: isinstance(context.sender, TempSender), )


def isPerson(
    id: Union[int, List[int]],
    inGroup: bool = False,
    fromGroup: bool = False,
) -> Censor:
    if isinstance(id, int):
        id = [id]

    def check(context: Context) -> bool:
        if isinstance(context.sender, FriendSender):
            return context.sender.id in id
        if inGroup and isinstance(context.sender, GroupSender):
            return context.sender.id in id
        if fromGroup and isinstance(context.sender, TempSender):
            return context.sender.id in id
        return False

    return Censor(check)


def isGroup(
    id: Union[int, List[int]],
    fromGroup: bool = False,
) -> Censor:
    if isinstance(id, int):
        id = [id]

    def check(context: Context) -> bool:
        if isinstance(context.sender, GroupSender):
            return context.sender.groupId in id
        elif fromGroup and isinstance(context.sender, TempSender):
            return context.sender.groupId in id
        return False

    return Censor(check)


def isGroupAdmin(includeOwner: bool = True, fromGroup: bool = True) -> Censor:
    if includeOwner:
        lst = ['OWNER', 'ADMINISTRATOR']
    else:
        lst = ['ADMINISTRATOR']

    def check(context: Context) -> bool:
        if isinstance(context.sender, GroupSender):
            return context.sender.permission in lst
        if fromGroup and isinstance(context.sender, TempSender):
            return context.sender.permission in lst
        return False

    return Censor(check)


def isGroupOwner(fromGroup: bool = True) -> Censor:
    def check(context: Context) -> bool:
        if isinstance(context.sender, GroupSender):
            return context.sender.permission == 'OWNER'
        if fromGroup and isinstance(context.sender, TempSender):
            return context.sender.permission == 'OWNER'
        return False

    return Censor(check)


def hasType(type: str) -> Censor:
    def check(context: Context) -> bool:
        return any(message.type == type for message in context.messageChain)

    return Censor(check)


def isAt(target: int) -> Censor:
    def check(context: Context) -> bool:
        return any(message.type == "At" and message['target'] == target
                   for message in context.messageChain)

    return Censor(check)
