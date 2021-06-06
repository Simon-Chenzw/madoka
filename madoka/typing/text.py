from __future__ import annotations

from typing import Literal, Optional, Type, get_args, get_origin

from pydantic import BaseModel  # pylint: disable=no-name-in-module


class Text(BaseModel, extra='forbid'):
    """
    auto choice subclass when instantiating
    __init__ of subclass should be compatible with pydantic
    :type: Used for type checking, but Text should not be instantiated
    """

    type: str

    class TypeMap:
        types: dict[str, Type[Text]] = {}
        extra: Type[Text]

        @classmethod
        def add(cls, name: str, cls_: Type[Text]) -> None:
            if name not in cls.types:
                cls.types[name] = cls_
            else:
                raise ValueError("type can't have same typename")

        @classmethod
        def get(cls, name: str) -> Type[Text]:
            return cls.types.get(name, cls.extra)

    def __init_subclass__(
        cls: Type[Text],
        **kwargs,
    ) -> None:
        if 'type' in cls.__fields__ and get_origin(
                cls.__fields__['type'].type_) is Literal:
            cls.TypeMap.add(
                get_args(cls.__fields__['type'].type_)[0],
                cls,
            )
        elif cls.__name__ == 'ExtraText':
            cls.TypeMap.extra = cls
        return super().__init_subclass__(**kwargs)

    def __new__(cls, *args, **kwargs) -> Type[Text]:
        if cls is Text:
            if 'type' in kwargs:
                return super().__new__(cls.TypeMap.get(kwargs['type']))
            else:
                return super().__new__(cls.TypeMap.extra)
        else:
            return super().__new__(cls)

    def __str__(self) -> str:
        return ''


class ExtraText(Text, extra='allow'):
    pass


class SourceText(Text):
    type: Literal['Source']
    id: int
    time: int


class QuoteText(Text):
    type: Literal['Quote']
    id: int
    groupId: int
    senderId: int
    targetId: int
    origin: list[Text]

    @property
    def originText(self) -> str:
        return ''.join(map(str, self.origin))

    @property
    def hasImage(self) -> bool:
        return '[图片]' in self.originText


class AtText(Text):
    type: Literal['At']
    target: int
    display: str

    def __str__(self) -> str:
        return self.display


class AtAllText(Text):
    type: Literal['AtAll']


class FaceText(Text):
    # TODO test
    type: Literal['Face']
    faceId: Optional[int]
    name: Optional[str]


class PlainText(Text):
    type: Literal['Plain']
    text: str

    def __init__(self, text: str, type: Literal['Plain'] = 'Plain') -> None:
        super().__init__(type=type, text=text)

    def __str__(self) -> str:
        return self.text


class ImageText(Text):
    type: Literal['Image']
    imageId: Optional[str]
    url: Optional[str]
    path: Optional[str]

    def __init__(
        self,
        path: Optional[str] = None,
        url: Optional[str] = None,
        imageId: Optional[str] = None,
        type: Literal['Image'] = 'Image',
    ) -> None:
        """
        :path: Need to be a relative path
        """
        super().__init__(path=path, url=url, imageId=imageId, type=type)


class FlashImageText(ImageText):
    type: Literal['FlashImage']


# TODO more Text type
