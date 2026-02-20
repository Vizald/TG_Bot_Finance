import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.types.error_event import ErrorEvent

from config import BOT_TOKEN_ENV
from constants import ERR_INTERNAL
from handlers import main_router
from database import init_db


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    logger = logging.getLogger(__name__)

    token = os.getenv(BOT_TOKEN_ENV)
    if not token:
        raise RuntimeError(f"Не задана переменная окружения: {BOT_TOKEN_ENV}")

    init_db()

    bot = Bot(token=token)
    dp = Dispatcher()

    async def on_dispatcher_error(event: ErrorEvent) -> None:
        logger.exception("dispatcher_unhandled_error", exc_info=event.exception)
        if event.update and event.update.message:
            await event.update.message.answer(ERR_INTERNAL)

    dp.error.register(on_dispatcher_error)
    dp.include_router(main_router)
    await bot.delete_my_commands()
    await bot.set_my_commands([
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="expense", description="Добавить расход: /expense сумма описание"),
        BotCommand(command="income", description="Добавить доход: /income сумма описание"),
        BotCommand(command="stats", description="Показать статистику"),
        BotCommand(command="help", description="Помощь"),
    ])
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")
