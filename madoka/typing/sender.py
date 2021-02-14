from typing import Any, Dict, Literal, Union

Sender = Union['FriendSender', 'GroupSender', 'TempSender']


class SenderBase:
    def __init__(self, json: Dict[str, Any]) -> None:
        self._json = json

    def __getitem__(self, key: str) -> Any:
        return self._json[key]

    @property
    def id(self) -> int:
        return self['id']

    @staticmethod
    def trans(
        messsageType: Literal['FriendMessage', 'GroupMessage', 'TempMessage'],
        json: Dict[str, Any],
    ) -> Sender:
        if messsageType == 'FriendMessage':
            return FriendSender(json)
        elif messsageType == 'GroupMessage':
            return GroupSender(json)
        elif messsageType == 'TempMessage':
            return TempSender(json)
        else:
            raise ValueError(
                "sender's messsageType must be: 'FriendMessage', 'GroupMessage', 'TempMessage'"
            )


class FriendSender(SenderBase):
    @property
    def name(self) -> str:
        return self['nickname']

    @property
    def remark(self) -> str:
        return self['remark']


class GroupSender(SenderBase):
    @property
    def name(self) -> str:
        return self['memberName']

    @property
    def permission(self) -> Literal['OWNER', 'ADMINISTRATOR', 'MEMBER']:
        return self['permission']

    @property
    def groupId(self) -> int:
        return self['group']['id']

    @property
    def groupName(self) -> str:
        return self['group']['name']

    @property
    def selfPermission(self) -> Literal['OWNER', 'ADMINISTRATOR', 'MEMBER']:
        return self['group']['permission']


class TempSender(SenderBase):
    @property
    def name(self) -> str:
        return self['memberName']

    @property
    def permission(self) -> Literal['OWNER', 'ADMINISTRATOR', 'MEMBER']:
        return self['permission']

    @property
    def groupId(self) -> int:
        return self['group']['id']

    @property
    def groupName(self) -> str:
        return self['group']['name']

    @property
    def selfPermission(self) -> Literal['OWNER', 'ADMINISTRATOR', 'MEMBER']:
        return self['group']['permission']
