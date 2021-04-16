import asyncio
import logging
import sys
import time
from typing import TYPE_CHECKING, Any, Awaitable, Dict, Optional, TypeVar, Literal

import requests

from .exception import MadokaInitError, MadokaRuntimeError

if TYPE_CHECKING:
    from .bot import QQbot

T = TypeVar('T')

logger = logging.getLogger('madoka')

# TODO autologin & offline detect


class BotBase:
    def __init__(
        self,
        qid: int,
        socket: str,
        authKey: str,
        bot: 'QQbot',
        adminQid: Optional[int] = None,
        waitMirai: Optional[int] = None,
        protocol: Literal['http', 'https'] = 'http',
        ws_protocol: Literal['ws', 'wss'] = 'ws',
    ) -> None:
        super().__init__()
        self.qid = qid
        self.adminQid = adminQid
        self._socket = socket
        self._authKey = authKey
        self._waitMirai = waitMirai
        self._protocol = protocol
        self._ws_protocol = ws_protocol
        # self._bot just use for typing hinting
        self._bot = bot

    def __enter__(self) -> 'BotBase':
        if sys.version_info.minor < 8:
            logger.error('Wrong python version, requires python>=3.8')
            raise MadokaInitError("Requires python version >= 3.8")
        self._getSession()
        logger.debug("get event loop")
        self._loop = asyncio.get_event_loop()
        return self

    def create_task(self, cor: Awaitable[T]) -> Awaitable[T]:
        """
        shortcut of `asyncio.get_event_loop().create_task(cor)`
        """
        return self._loop.create_task(cor)

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        self._releaseSession()
        return False

    def _getSession(self) -> None:
        def checkApi() -> None:
            cnt = 0
            if self._waitMirai is None:
                try:
                    res = requests.get(
                        f"{self._protocol}://{self._socket}/about").json()
                    logger.info(f"api version: {res['data']['version']}")
                except:
                    logger.error("Unable to connect to mirai-api-http")
                    raise MadokaInitError(
                        "Unable to connect to mirai-api-http")
            else:
                while not (cnt and cnt == self._waitMirai):
                    try:
                        cnt += 1
                        res = requests.get(
                            f"{self._protocol}://{self._socket}/about").json()
                    except:
                        logger.info(f"get api information failed: {cnt} times")
                        time.sleep(3)
                    else:
                        logger.info(f"api version: {res['data']['version']}")
                        break
                else:
                    logger.error("Unable to connect to mirai-api-http")
                    raise MadokaInitError(
                        "Unable to connect to mirai-api-http")
                if cnt: time.sleep(3)

        def apiPost(interface: str, **data: Any) -> Dict[str, Any]:
            try:
                res = requests.post(
                    url=f"{self._protocol}://{self._socket}/{interface}",
                    json=data,
                ).json()
                if res['code']:
                    code = res['code']
                    msg = res.get('msg', 'unknown')
                    logger.error(f'{interface} failed: {code=} {msg=}')
                    raise MadokaInitError(f'{interface} failed')
            except Exception as err:
                logger.error(
                    f'{interface} failed: <{err.__class__.__name__}> {err}')
                raise MadokaInitError(f'{interface} failed')
            logger.debug(f'{interface} success')
            return res

        try:
            # check api connection
            checkApi()
            # auth
            self._session = apiPost('auth', authKey=self._authKey)['session']
            # verify
            apiPost('verify', sessionKey=self._session, qq=self.qid)
            # set config
            apiPost(
                'config',
                sessionKey=self._session,
                cacheSize=4096,
                enableWebsocket=True,
            )
            logger.info(
                f"successfully authenticate: sessionKey={self._session}")
        except MadokaInitError:
            raise
        except:
            raise MadokaInitError("Can't get sessionKey")

    def _releaseSession(self) -> None:
        try:
            res = requests.post(
                url=f"{self._protocol}://{self._socket}/release",
                json={
                    "sessionKey": self._session,
                    "qq": self.qid,
                },
            ).json()
            if res['code']:
                code = res['code']
                msg = res.get('msg', 'unknown')
                logger.error(f'release sessionKey failed: {code=} {msg=}')
                raise MadokaRuntimeError('release sessionKey failed') from None
        except:
            logger.exception(f'release sessionKey failed:')
            raise MadokaRuntimeError('release sessionKey failed')
        else:
            logger.info(f"Successful release")
