from __future__ import annotations

from typing import TYPE_CHECKING, List, Union, Type

from ..typing import AtText, Context, FriendSender, GroupSender, TempSender, Text

if TYPE_CHECKING:
    from ..bot import QQbot
    from ..typing.frame import contextCheckFunc


class Censor:
    def __init__(self, check: contextCheckFunc) -> None:
        self.check = check

    def __call__(self, bot: QQbot, context: Context) -> bool:
        return self.check(bot, context)

    def __eq__(self, rhs: Censor) -> Censor:
        return Censor(lambda bot, context: self.check(bot, context) == rhs.
                      check(bot, context))

    def __nq__(self, rhs: Censor) -> Censor:
        return Censor(lambda bot, context: self.check(bot, context) != rhs.
                      check(bot, context))

    def __and__(self, rhs: Censor) -> Censor:
        return Censor(lambda bot, context: self.check(bot, context) and rhs.
                      check(bot, context))

    def __or__(self, rhs: Censor) -> Censor:
        return Censor(lambda bot, context: self.check(bot, context) or rhs.
                      check(bot, context))

    def __invert__(self) -> Censor:
        return Censor(lambda bot, context: not self.check(bot, context))


isFriendMessage = Censor(
    lambda bot, context: isinstance(context.sender, FriendSender))
isGroupMessage = Censor(
    lambda bot, context: isinstance(context.sender, GroupSender))
isTempMessage = Censor(
    lambda bot, context: isinstance(context.sender, TempSender))


def isAdmin(
    inGroup: bool = False,
    fromGroup: bool = False,
) -> Censor:
    def check(bot: QQbot, context: Context) -> bool:
        if bot.adminQid:
            if isinstance(context.sender, FriendSender):
                return context.sender.id == bot.adminQid
            elif inGroup and isinstance(context.sender, GroupSender):
                return context.sender.id == bot.adminQid
            elif fromGroup and isinstance(context.sender, TempSender):
                return context.sender.id == bot.adminQid
        return False

    return Censor(check)


def isPerson(
    id: Union[int, List[int]],
    inGroup: bool = False,
    fromGroup: bool = False,
) -> Censor:
    if isinstance(id, int):
        id = [id]

    def check(bot: QQbot, context: Context) -> bool:
        if isinstance(context.sender, FriendSender):
            return context.sender.id in id
        elif inGroup and isinstance(context.sender, GroupSender):
            return context.sender.id in id
        elif fromGroup and isinstance(context.sender, TempSender):
            return context.sender.id in id
        return False

    return Censor(check)


def isGroup(
    id: Union[int, List[int]],
    fromGroup: bool = False,
) -> Censor:
    if isinstance(id, int):
        id = [id]

    def check(bot: QQbot, context: Context) -> bool:
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

    def check(bot: QQbot, context: Context) -> bool:
        if isinstance(context.sender, GroupSender):
            return context.sender.permission in lst
        elif fromGroup and isinstance(context.sender, TempSender):
            return context.sender.permission in lst
        return False

    return Censor(check)


def isGroupOwner(fromGroup: bool = True) -> Censor:
    def check(bot: QQbot, context: Context) -> bool:
        if isinstance(context.sender, GroupSender):
            return context.sender.permission == 'OWNER'
        elif fromGroup and isinstance(context.sender, TempSender):
            return context.sender.permission == 'OWNER'
        return False

    return Censor(check)


# TODO rewrite
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


def isText(s: str) -> Censor:
    return Censor(lambda bot, context: context.text == s)


def isTextStartWith(s: str) -> Censor:
    return Censor(lambda bot, context: context.text[:len(s)] == s)


def isTextEndWith(s: str) -> Censor:
    return Censor(lambda bot, context: context.text[-len(s):] == s)
