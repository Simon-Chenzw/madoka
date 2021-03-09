import asyncio
import logging
import sys

from madoka import QQbot
from madoka.register import register, timedRegister, runOnce
from madoka.filter import isAdmin, isGroupMessage, isText
from madoka.typing import Context

if 'debug' in sys.argv:
    logging.getLogger().setLevel(logging.DEBUG)
else:
    logging.getLogger().setLevel(logging.INFO)

logger = logging.getLogger('madoka')


@timedRegister(runOnce())
def helloworld(bot: QQbot):
    bot.sendToAdmin(message='奇跡も、魔法も、あるんだよ', )


@register((isAdmin(True) | ~isGroupMessage) & isText('ping'))
def ping(bot: QQbot, context: Context) -> None:
    logger.info(f"ping from {context.sender.id}")
    bot.reply('pong')


@register(isAdmin(True) & isText('stop'))
async def stop(bot: QQbot, context: Context) -> None:
    bot.reply('Madoka will stop')
    await asyncio.sleep(3)
    bot.stop()


try:
    with QQbot(
            qid=12345,
            adminQid=123456,
            socket="127.0.0.1:1080",
            authKey="authKey",
    ) as bot:
        bot.working()
except Exception as err:
    print(err.__class__.__name__, err)
