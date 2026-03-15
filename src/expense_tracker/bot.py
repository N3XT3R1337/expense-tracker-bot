import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from .config import load_config
from .handlers.callbacks import router as callbacks_router
from .handlers.commands import router as commands_router
from .models.base import create_tables, init_engine


async def main():
    config = load_config()

    if not config.bot_token:
        logging.error("BOT_TOKEN environment variable is not set")
        sys.exit(1)

    init_engine(config.database_url)
    await create_tables()

    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(commands_router)
    dp.include_router(callbacks_router)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )

    logging.info("Bot starting...")
    await dp.start_polling(bot)


def run():
    asyncio.run(main())


if __name__ == "__main__":
    run()
