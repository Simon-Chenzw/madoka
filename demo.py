import asyncio
import logging

from madoka import QQbot
from madoka.filter import isAdmin, isGroupMessage, isText
from madoka.typing import Context

logging.basicConfig(level=logging.INFO, format="%(message)s")

logger = logging.getLogger(__name__)

bot = QQbot(123456, "127.0.0.1:80", "verifyKey", adminQid=12345)


@bot.runOnce()
def helloworld(bot: QQbot):
    bot.sendToAdmin(message='奇跡も、魔法も、あるんだよ', )


@bot.addFunction((isAdmin | ~isGroupMessage) & isText('^ping$'))
def ping(bot: QQbot, context: Context) -> None:
    logger.info(f"ping from {context.sender.id}")
    bot.reply('pong')


@bot.addFunction(isAdmin & isText('^stop$'))
async def stop(bot: QQbot, context: Context) -> None:
    bot.reply('Madoka will stop')
    await asyncio.sleep(3)
    bot.stop()


bot.simple_running()
