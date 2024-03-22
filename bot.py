# библиотеки
import asyncio
import logging 
from aiogram import Bot, Dispatcher, types

# конфиг
from config.config import token

# обработчики
from app.handlers.database_work import register_database_work

logger = logging.getLogger(__name__)
async def main():
    # настройка логирования
    logging.basicConfig(
        level= logging.INFO, 
        format= "%(asctime)s - %(levelname)s - %(levelname)s - %(message)s"
    )
    logger.info("Logging started work")

    # инициализация бота
    bot = Bot(token= token)
    dp = Dispatcher(bot= bot)

    # установка команд
    commands = [
        types.BotCommand(command= "/start", description= "Начало работы")
    ]
    await bot.set_my_commands(commands)

    # включение обработчиков
    await register_database_work(dp)

    # начало работы
    await dp.start_polling()
    logger.info("Bot started work")

if __name__ == "__main__":
    asyncio.run(main())