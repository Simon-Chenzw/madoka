from __future__ import annotations

from typing import Any, Dict, List, Optional, Type, TypeVar

T = TypeVar('T')


class Text:
    def __init__(self, json: Dict[str, Any]) -> None:
        self._json = json

    def __getitem__(self, key: str) -> Any:
        return self._json[key]

    def __str__(self) -> str:
        return ''

    @property
    def serialize(self):
        return self._json

    @classmethod
    def deserialize(cls: Type[T], json: Dict[str, Any]) -> T:
        obj = cls.__new__(cls)
        obj._json = json
        return obj

    @property
    def type(self) -> str:
        return self['type']

    @staticmethod
    def trans(json: Dict[str, Any]) -> Text:
        if json['type'] == "Source":
            return SourceText.deserialize(json)
        elif json['type'] == "Plain":
            return PlainText.deserialize(json)
        elif json['type'] == "Image":
            return ImageText.deserialize(json)
        elif json['type'] == "Quote":
            return QuoteText.deserialize(json)
        elif json['type'] == "At":
            return AtText.deserialize(json)
        else:
            return Text(json)


class SourceText(Text):
    @property
    def id(self) -> int:
        return self['id']

    @property
    def time(self) -> int:
        return self['time']


class PlainText(Text):
    def __init__(self, text: str) -> None:
        super().__init__({
            "type": "Plain",
            "text": text,
        })

    def __str__(self) -> str:
        return self.text

    @property
    def text(self) -> str:
        return self['text']


class ImageText(Text):
    def __init__(
        self,
        path: Optional[str] = None,
        url: Optional[str] = None,
    ) -> None:
        """
        :path: Need to be a relative path
        """
        super().__init__({
            "type": "Image",
            "path": path,
            "url": url,
        })

    @property
    def path(self) -> Optional[str]:
        return self['path']

    @property
    def url(self) -> Optional[str]:
        return self['url']


class QuoteText(Text):
    _text: Optional[str] = None

    @property
    def id(self) -> int:
        return self['id']

    @property
    def group(self) -> int:
        return self['groupId']

    @property
    def sender(self) -> int:
        return self['senderId']

    @property
    def target(self) -> int:
        return self['targetId']

    @property
    def origin(self) -> List[Text]:
        return self['origin']

    @property
    def text(self) -> str:
        if self._text is None:
            self._text = ''.join(text['text'] for text in self.origin
                                 if text['type'] == "Plain")
        return self._text

    @property
    def hasImage(self) -> bool:
        return '[图片]' in self.text


class AtText(Text):
    def __str__(self) -> str:
        return self.display

    @property
    def target(self) -> int:
        return self['target']

    @property
    def display(self) -> str:
        return self['display']
