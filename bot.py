# Библиотеки
import asyncio # стандартная библиотека ассинхронного программирования
import logging # логирование, или запись событий в журнал
from aiogram import Bot, Dispatcher, types 
from aiogram.enums import ParseMode  
from aiogram.fsm.storage.memory import MemoryStorage # где хранятся состояния

# Конфиг
from config.bot_config import token

# Обработчики
from app.handlers import start
from app.handlers import database_work

logger = logging.getLogger(__name__)
async def main():
    # Настройка логирования
    logging.basicConfig(
        level= logging.INFO, 
        format= "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    logger.info("Логирование начало работу")

    # Инициализация бота
    bot = Bot(token= token, parse_mode= ParseMode.HTML)
    dp = Dispatcher(storage= MemoryStorage())

    # Установка команд
    commands = [
        types.BotCommand(command= "/start", description= "Начало работы")
    ]
    await bot.set_my_commands(commands)

    # Включение обработчиков
    dp.include_router(database_work.router)
    dp.include_router(start.router)

    # Начало работы
    logger.info("Бот начал работу")
    await dp.start_polling(bot)
    logger.info("Бот закончил работу")

if __name__ == "__main__":
    asyncio.run(main())