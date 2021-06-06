from typing import Literal

from pydantic import BaseModel  # pylint: disable=no-name-in-module


class GroupInfo(BaseModel):
    id: int
    name: str
    permission: Literal['OWNER', 'ADMINISTRATOR', 'MEMBER']


class Sender(BaseModel, extra='forbid'):
    """
    can't auto choice subclass when instantiating
    SenderBase should not be instantiated
    """
    id: int


class FriendSender(Sender):
    nickname: str
    remark: str


class GroupSender(Sender):
    memberName: str
    specialTitle: str
    permission: Literal['OWNER', 'ADMINISTRATOR', 'MEMBER']
    joinTimestamp: int
    lastSpeakTimestamp: int
    muteTimeRemaining: int
    group: GroupInfo


class TempSender(Sender):
    memberName: str
    specialTitle: str
    permission: Literal['OWNER', 'ADMINISTRATOR', 'MEMBER']
    joinTimestamp: int
    lastSpeakTimestamp: int
    muteTimeRemaining: int
    group: GroupInfo


class StrangerSender(Sender):
    nickname: str
    remark: str


class OtherClientSender(Sender):
    platform: str
