from typing import Literal, Union

from pydantic import BaseModel  # pylint: disable=no-name-in-module

Sender = Union['FriendSender', 'GroupSender', 'TempSender']

# TODO: rename Sender to User, for typing in Event (wait for mirai-api-http 2.0)


class GroupInfo(BaseModel):
    id: int
    name: str
    permission: Literal['OWNER', 'ADMINISTRATOR', 'MEMBER']


class SenderBase(BaseModel, extra='forbid'):
    """
    can't auto choice subclass when instantiating
    SenderBase should not be instantiated
    """
    id: int


class FriendSender(SenderBase):
    nickname: str
    remark: str


class GroupSender(SenderBase):
    memberName: str
    permission: Literal['OWNER', 'ADMINISTRATOR', 'MEMBER']
    group: GroupInfo


class TempSender(SenderBase):
    memberName: str
    permission: Literal['OWNER', 'ADMINISTRATOR', 'MEMBER']
    group: GroupInfo
