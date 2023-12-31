# библиотеки
import asyncio
import logging 
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# конфиг
from config.bot_config import token

# обработчики
from app.handlers.start import register_start

logger = logging.getLogger(__name__)
async def main():
    # настройка логирования
    logging.basicConfig(
        level= logging.INFO, 
        format= "%(asctime)s - %(levelname)s - %(levelname)s - %(message)s"
    )
    logger.info("Logging started work")

    # инициализация бота
    bot = Bot(token= token, parse_mode= types.ParseMode.HTML)
    dp = Dispatcher(bot, storage= MemoryStorage())

    # установка команд
    commands = [
        types.BotCommand(command= "/start", description= "Начало работы")
    ]
    await bot.set_my_commands(commands)

    # включение обработчиков
    await register_start(dp)

    # начало работы
    await dp.start_polling()
    logger.info("Bot started work")

if __name__ == "__main__":
    asyncio.run(main())