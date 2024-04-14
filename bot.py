# библиотеки
import asyncio
import logging 
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage

# конфиг
from config.bot_config import token

# обработчики
from app.handlers import start
from app.handlers import database_work


logger = logging.getLogger(__name__)
async def main():
    # настройка логирования
    logging.basicConfig(
        level= logging.INFO, 
        format= "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    logger.info("Логирование начало работу")

    # инициализация бота
    bot = Bot(token= token)
    dp = Dispatcher(storage= MemoryStorage())

    # установка команд
    commands = [
        types.BotCommand(command= "/start", description= "Начало работы")
    ]
    await bot.set_my_commands(commands)

    # включение обработчиков
    dp.include_router(database_work.router)
    dp.include_router(start.router)

    # начало работы
    logger.info("Бот начал работу")
    await dp.start_polling(bot)
    logger.info("Бот закончил работу")

if __name__ == "__main__":
    asyncio.run(main())