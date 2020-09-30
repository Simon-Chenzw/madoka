"""
demo of qqbot
"""
from __future__ import absolute_import

import logging

#The following should be import from madoka
from .bot import QQbot
from .data import Context
from .filter import Censor, auth, isFriendMessage, isTempMessage
from .register import register, runOnce

logger = logging.getLogger(__name__)


@runOnce()
def helloworld(bot: QQbot):
    if adminQQ:
        bot.sendFriendMessage(
            target=adminQQ,
            message='奇跡も、魔法も、あるんだよ',
        )


isPing = Censor(lambda context: context.messageChain[1].type == 'Plain' and
                context.messageChain[1]['text'] == 'ping')


@register
@auth((isFriendMessage | isTempMessage) & isPing)
def ping(bot: QQbot, context: Context) -> None:
    logger.info(f"ping from {context.sender.id}")
    bot.reply(context.sender, "pong")


@register
@auth(isFriendMessage & (~isPing))
def repeat(bot: QQbot, data: Context):
    text = ''.join(message['text'] for message in data.messageChain
                   if message.type == 'Plain')
    bot.reply(sender=data.sender, message=text)
    logger.info(f"reply {data.sender.name} {text}")


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
