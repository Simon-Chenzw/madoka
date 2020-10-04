from __future__ import absolute_import

import logging
from typing import Optional

import requests

from .base import BotBase
from .data import Context

logger = logging.getLogger(__name__)


class getUnit(BotBase):
    def messageFromId(self, id: int) -> Optional[Context]:
        try:
            res = requests.get(
                url=f"http://{self.socket}/messageFromId",
                params={
                    "sessionKey": self.session,
                    "id": id,
                },
            ).json()
        except Exception as err:
            logger.warn(f"messageFromId crashed: {err}")
            return None
        else:
            logger.debug(f"messageFromId: id={id} res={res}")
            if res['code']:
                logger.warn(f"messageFromId failed: {res['msg']}")
                return None
            else:
                return Context(res['data'])
