import aioschedule
import bot
import asyncio
import logging
from aiogram.utils import executor
import db_processing

logging.basicConfig(level=logging.INFO)


async def scheduler():
    aioschedule.every(0.5).minutes.do(db_processing.EventsChecker)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(0.1)


async def StartUp(_):
    asyncio.create_task(scheduler())


if __name__ == '__main__':
    executor.start_polling(bot.dp, skip_updates=True, on_startup=StartUp)
