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
        logger.info("get event loop")
        self.loop = asyncio.get_event_loop()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        self._releaseSession()
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
            logger.error(f"auth error: code={res['code']}")
            raise Exception("error during auth")
        else:
            logger.info(f"Successfully authenticate: session={res['session']}")
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
            logger.error(f"verify error: code={res['code']}")
            raise Exception("error during verify")
        else:
            logger.info(f"Successfully verified")

    def _releaseSession(self) -> None:
        res = requests.post(
            url=f"http://{self.socket}/release",
            json={
                "sessionKey": self.session,
                "qq": self.qid,
            },
        ).json()
        if res['code']:
            logger.error(f"release error: code={res['code']}")
            raise Exception("error during release")
        else:
            logger.info(f"Successful release")
