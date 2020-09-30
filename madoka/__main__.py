"""
demo of qqbot
"""
from __future__ import absolute_import
import logging

from .bot import QQbot
from .filter import auth, isFriendMessage
from .register import register
from .data import Context

logger = logging.getLogger(__name__)


@register
@auth(isFriendMessage)
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
        bot.working()
