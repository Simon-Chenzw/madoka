from __future__ import annotations

import re
from typing import TYPE_CHECKING, Callable, Type, Union

from .typing import AtText, Context, GroupSender, TempSender, Text

if TYPE_CHECKING:
    from .bot import QQbot


class Censor:
    def __init__(self, check: Callable[[QQbot, Context], bool]) -> None:
        self.check = check

    def __call__(self, bot: QQbot, ctx: Context) -> bool:
        return self.check(bot, ctx)

    def __eq__(self, rhs: Censor) -> Censor:
        return Censor(lambda bot, ctx: self(bot, ctx) == rhs(bot, ctx))

    def __nq__(self, rhs: Censor) -> Censor:
        return Censor(lambda bot, ctx: self(bot, ctx) != rhs(bot, ctx))

    def __and__(self, rhs: Censor) -> Censor:
        return Censor(lambda bot, ctx: self(bot, ctx) and rhs(bot, ctx))

    def __or__(self, rhs: Censor) -> Censor:
        return Censor(lambda bot, ctx: self(bot, ctx) or rhs(bot, ctx))

    def __invert__(self) -> Censor:
        return Censor(lambda bot, ctx: not self(bot, ctx))


def isMessage(
    isFriend: bool = True,
    isGroup: bool = True,
    isTemp: bool = True,
) -> Censor:
    def check(bot: QQbot, ctx: Context) -> bool:
        if ctx.type == "FriendMessage":
            return isFriend
        elif ctx.type == "GroupMessage":
            return isGroup
        elif ctx.type == "TempMessage":
            return isTemp
        else:
            return False

    return Censor(check)


isFriendMessage = Censor(lambda bot, ctx: ctx.type == "FriendMessage")
isGroupMessage = Censor(lambda bot, ctx: ctx.type == "GroupMessage")
isTempMessage = Censor(lambda bot, ctx: ctx.type == "TempMessage")


def isAdminCheck(bot: QQbot, ctx: Context) -> bool:
    if bot.adminQid and ctx.sender.id == bot.adminQid:
        return True
    else:
        return False


isAdmin = Censor(isAdminCheck)


def isPerson(id: int | list[int]) -> Censor:
    _id = [id] if isinstance(id, int) else id

    def check(bot: QQbot, ctx: Context) -> bool:
        if ctx.sender.id in _id:
            return True
        return False

    return Censor(check)


def inGroup(id: Union[int, list[int]]) -> Censor:
    _id = [id] if isinstance(id, int) else id

    def check(bot: QQbot, context: Context) -> bool:
        if isinstance(context.sender, GroupSender):
            return context.sender.group.id in _id
        elif isinstance(context.sender, TempSender):
            return context.sender.group.id in _id
        return False

    return Censor(check)


def isGroup(id: Union[int, list[int]]) -> Censor:
    _id = [id] if isinstance(id, int) else id

    def check(bot: QQbot, context: Context) -> bool:
        if isinstance(context.sender, GroupSender):
            return context.sender.group.id in _id
        return False

    return Censor(check)


def fromGroup(id: Union[int, list[int]]) -> Censor:
    _id = [id] if isinstance(id, int) else id

    def check(bot: QQbot, context: Context) -> bool:
        if isinstance(context.sender, TempSender):
            return context.sender.group.id in _id
        return False

    return Censor(check)


def isGroupAdmincheck(bot: QQbot, context: Context) -> bool:
    if isinstance(context.sender, GroupSender):
        return context.sender.permission in ['OWNER', 'ADMINISTRATOR']
    elif isinstance(context.sender, TempSender):
        return context.sender.permission in ['OWNER', 'ADMINISTRATOR']
    return False


isGroupAdmin = Censor(isGroupAdmincheck)


def isGroupOwnercheck(bot: QQbot, context: Context) -> bool:
    if isinstance(context.sender, GroupSender):
        return context.sender.permission == 'OWNER'
    elif fromGroup and isinstance(context.sender, TempSender):
        return context.sender.permission == 'OWNER'
    return False


isGroupOwner = Censor(isGroupOwnercheck)


def hasType_str(type: str) -> Censor:
    def check(bot: QQbot, context: Context) -> bool:
        for text in context.messageChain:
            if text.type == type:
                return True
        return False

    return Censor(check)


def hasType(type: Type[Text]) -> Censor:
    return Censor(lambda bot, context: context.get(type) is not None)


def isAt(target: int) -> Censor:
    def check(bot: QQbot, context: Context) -> bool:
        for text in context.iter(AtText):
            if text.target == target:
                return True
        return False

    return Censor(check)


def selfAtcheck(bot: QQbot, context: Context) -> bool:
    for text in context.iter(AtText):
        if text.target == bot.qid:
            return True
    return False


isAtSelf = Censor(selfAtcheck)


def isText(regExp: str) -> Censor:
    """
    use `re.search`
    """
    def check(bot: QQbot, ctx: Context) -> bool:
        if re.search(regExp, ctx.text):
            return True
        return False

    return Censor(check)
