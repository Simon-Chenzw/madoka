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
        type_key: str = 'type'
        types: dict[str, Type[Text]] = {}
        extra_name: str = 'ExtraText'
        extra: Type[Text]

        @classmethod
        def add(cls, ins_cls: Type[Text]) -> None:
            if ins_cls.__name__ == cls.extra_name:
                cls.extra = ins_cls
                return

            field = ins_cls.__fields__.get(cls.type_key)
            if field is None:
                return

            if get_origin(field.type_) is Literal:
                for name in get_args(field.type_):
                    assert name not in cls.types, "can't have same key value"
                    cls.types[name] = ins_cls

    def __init_subclass__(cls, **kwargs) -> None:
        cls.TypeMap.add(cls)
        return super().__init_subclass__()

    def __new__(cls, *args, **kwargs) -> Type[Text]:
        key = cls.TypeMap.type_key
        if cls is Text:
            if key in kwargs:
                new_cls = cls.TypeMap.types.get(kwargs[key], cls.TypeMap.extra)
                return super().__new__(new_cls)
            else:
                return super().__new__(cls.TypeMap.extra)  # type: ignore
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
    target: int


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
    base64: Optional[str]

    def __init__(
        self,
        path: Optional[str] = None,
        url: Optional[str] = None,
        imageId: Optional[str] = None,
        base64: Optional[str] = None,
        type: Literal['Image'] = 'Image',
    ) -> None:
        """
        :path: Need to be a relative path
        """
        super().__init__(
            path=path,
            url=url,
            imageId=imageId,
            type=type,
            base64=base64,
        )


class FlashImageText(ImageText):
    type: Literal['FlashImage']


# TODO more Text type
