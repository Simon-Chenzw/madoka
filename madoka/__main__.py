"""
demo of qqbot
"""
from __future__ import absolute_import

import logging

#The following should be import from madoka
from .bot import QQbot
from .data import Context
from .filter import Censor, isFriendMessage, isTempMessage
from .register import register, runOnce

logger = logging.getLogger(__name__)


@runOnce()
def helloworld(bot: QQbot):
    if adminQQ:
        bot.sendFriendMessage(
            target=adminQQ,
            message='奇跡も、魔法も、あるんだよ',
        )


isPing = Censor(lambda context: context.text == 'ping')


@register((isFriendMessage | isTempMessage) & isPing)
def ping(bot: QQbot, context: Context) -> None:
    logger.info(f"ping from {context.sender.id}")
    bot.reply(context.sender, "pong")


@register(isFriendMessage & ~isPing)
def repeat(bot: QQbot, context: Context):
    logger.info(f"reply {context.sender.name} {context.text}")
    bot.reply(context.sender, context.text)


if __name__ == "__main__":
    logging.basicConfig(
        format="[%(asctime)s] %(levelname)s %(message)s",
        level=logging.INFO,
    )

    with QQbot(
            qid=123456789,
            socket="{ip}:{port}",
            authKey="mirai-api-http",
            autoRegister=True,
    ) as bot:
        adminQQ = 0
        bot.working()
