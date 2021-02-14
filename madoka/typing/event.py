import json
from typing import Any, Dict, Union


class Event:
    def __init__(self, message: Union[str, Dict[str, Any]]) -> None:
        if isinstance(message, str):
            self._json = json.loads(message)
        else:
            self._json = message

    def __getitem__(self, key: str) -> Any:
        return self._json[key]

    @property
    def serialize(self):
        return self._json

    @property
    def type(self) -> str:
        return self['type']
