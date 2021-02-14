from typing import Optional


class MadokaError(Exception):
    def __init__(self, message: Optional[str] = None):
        self.message = message or "Madoka got an Error"

    def __str__(self) -> str:
        return self.message


class MadokaInitError(MadokaError):
    def __init__(self, message: Optional[str] = None):
        self.message = message or "Madoka initialize failed"


class MadokaRuntimeError(MadokaError):
    def __init__(self, message: Optional[str] = None):
        self.message = message or "Madoka got an RuntimeError"
