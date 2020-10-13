from __future__ import absolute_import

import asyncio
import logging

import requests

logger = logging.getLogger(__name__)


class BotBase:
    def __init__(
        self,
        qid: int,
        socket: str,
        authKey: str,
        adminQQ: int = 0,
    ) -> None:
        super().__init__()
        self.qid = qid
        self.socket = socket
        self.authKey = authKey

    def __enter__(self) -> 'BotBase':
        self._auth()
        self._verify()
        logger.info(f"successfully authenticate: session={self.session}")
        logger.debug("get event loop")
        self.loop = asyncio.get_event_loop()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        try:
            self._releaseSession()
        except Exception as err:
            logger.warning(f"cannot release session because of {err}")
        return False

    def _auth(self) -> None:
        # TODO: retry several times
        res = requests.post(
            url=f"http://{self.socket}/auth",
            json={
                "authKey": self.authKey
            },
        ).json()
        if res['code']:
            logger.critical(f"auth error: code={res['code']}")
            raise Exception("error during auth")
        self.session = res['session']

    def _verify(self) -> None:
        res = requests.post(
            url=f"http://{self.socket}/verify",
            json={
                "sessionKey": self.session,
                "qq": self.qid,
            },
        ).json()
        if res['code']:
            logger.critical(f"verify error: code={res['code']}")
            raise Exception("error during verify")

    def _releaseSession(self) -> None:
        res = requests.post(
            url=f"http://{self.socket}/release",
            json={
                "sessionKey": self.session,
                "qq": self.qid,
            },
        ).json()
        if res['code']:
            logger.critical(f"release error: code={res['code']}")
            raise Exception("error during release")
        else:
            logger.info(f"Successful release")
