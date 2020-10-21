from __future__ import absolute_import

import asyncio
import logging
from typing import TYPE_CHECKING

import requests

if TYPE_CHECKING:
    from .bot import QQbot

logger = logging.getLogger(__name__)


class BotBase:
    def __init__(
        self,
        qid: int,
        socket: str,
        authKey: str,
        bot: 'QQbot',
    ) -> None:
        super().__init__()
        self.qid = qid
        self._socket = socket
        self._authKey = authKey
        # self._bot just use for typing hinting
        self._bot = bot

    def __enter__(self) -> 'BotBase':
        self._auth()
        self._verify()
        logger.info(f"successfully authenticate: session={self._session}")
        logger.debug("get event loop")
        self._loop = asyncio.get_event_loop()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        try:
            self._releaseSession()
        except Exception as err:
            logger.warning(f"cannot release session")
        return False

    def _auth(self) -> None:
        # TODO: retry several times
        res = requests.post(
            url=f"http://{self._socket}/auth",
            json={
                "authKey": self._authKey
            },
        ).json()
        if res['code']:
            logger.critical(f"auth error: code={res['code']}")
            raise Exception("error during auth")
        self._session = res['session']

    def _verify(self) -> None:
        res = requests.post(
            url=f"http://{self._socket}/verify",
            json={
                "sessionKey": self._session,
                "qq": self.qid,
            },
        ).json()
        if res['code']:
            logger.critical(f"verify error: code={res['code']}")
            raise Exception("error during verify")

    def _releaseSession(self) -> None:
        res = requests.post(
            url=f"http://{self._socket}/release",
            json={
                "sessionKey": self._session,
                "qq": self.qid,
            },
        ).json()
        if res['code']:
            logger.critical(f"release error: code={res['code']}")
            raise Exception("error during release")
        else:
            logger.info(f"Successful release")
