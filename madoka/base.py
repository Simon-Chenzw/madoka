from __future__ import absolute_import

import asyncio
import logging
import time
from typing import TYPE_CHECKING, Optional

import requests

from .exception import MadokaInitError

if TYPE_CHECKING:
    from .bot import QQbot

logger = logging.getLogger(__name__)

# TODO autologin & offline detect

class BotBase:
    def __init__(
        self,
        qid: int,
        socket: str,
        authKey: str,
        bot: 'QQbot',
        waitMirai: Optional[int] = None,
    ) -> None:
        super().__init__()
        self.qid = qid
        self._socket = socket
        self._authKey = authKey
        self._waitMirai = waitMirai
        # self._bot just use for typing hinting
        self._bot = bot

    def __enter__(self) -> 'BotBase':
        if isinstance(self._waitMirai, int):
            self._wait()
        self._auth()
        self._verify()
        self._setConfig()
        logger.info(f"successfully authenticate: sessionKey={self._session}")
        logger.debug("get event loop")
        self._loop = asyncio.get_event_loop()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        try:
            self._releaseSession()
        except Exception as err:
            logger.warning(f"cannot release session")
        return False

    def _wait(self) -> None:
        cnt = 0
        while not (cnt and cnt == self._waitMirai):
            try:
                cnt += 1
                res = requests.get(f"http://{self._socket}/about").json()
            except:
                logger.info(f"get api information failed: {cnt} times")
                time.sleep(3)
            else:
                logger.info(f"api version: {res['data']['version']}")
                time.sleep(1)
                return

    def _auth(self) -> None:
        res = requests.post(
            url=f"http://{self._socket}/auth",
            json={
                "authKey": self._authKey
            },
        ).json()
        if res['code']:
            logger.critical(f"auth error: code={res['code']}")
            raise MadokaInitError(res.get('msg', "during auth"))
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
            raise MadokaInitError(res.get('msg', "during verify"))

    def _setConfig(self) -> None:
        res = requests.post(
            f"http://{self._socket}/config",
            json={
                "sessionKey": self._session,
                "cacheSize": 4096,
                "enableWebsocket": True,
            },
        ).json()
        if res['code']:
            logger.critical(f"set config error: code={res['code']}")
            raise MadokaInitError(res.get('msg', "during set config"))

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
            raise Exception("can't release sessionKey")
        else:
            logger.info(f"Successful release")
