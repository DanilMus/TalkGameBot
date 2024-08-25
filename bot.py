# 
# | Файл настройки бота |
# 

# Библиотеки
from aiogram import Bot, Dispatcher, types, BaseMiddleware
from aiogram.types import TelegramObject
from aiogram.enums import ParseMode  
from aiogram.fsm.strategy import FSMStrategy
from aiogram.fsm.storage.memory import MemoryStorage # где хранятся состояния
from aiogram.client.default import DefaultBotProperties

import asyncio # стандартная библиотека ассинхронного программирования
import logging # логирование, или запись событий в журнал
from typing import Any, Callable, Dict, Awaitable # Для мидлвари

# Конфиг
from config.config_reader import config

# Обработчики
from app.handlers import start
from app.handlers import database_work
from app.handlers import game


# Outer-мидлварь, чтобы был ответ на колбэки
# (чтобы игрок видел, что обработка запроса пошла)
class CallbackResponseMiddleware(BaseMiddleware):
    async def __call__(
            self, 
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], 
            event: TelegramObject, 
            data: Dict[str, Any]
    ) -> Any:
        await event.answer()
        return await handler(event, data)


logger = logging.getLogger(__name__)
async def main():
    # Настройка логирования
    logging.basicConfig(
        level= logging.INFO, 
        format= "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    logger.info("Логирование начало работу")

    # Инициализация бота
    bot = Bot(token= config.bot_token.get_secret_value(), default= DefaultBotProperties(parse_mode= ParseMode.HTML))
    dp = Dispatcher(storage= MemoryStorage(), fsm_strategy= FSMStrategy.CHAT)

    # Установка команд
    commands = [
        types.BotCommand(command= "/start", description= "Начало работы"),
        types.BotCommand(command= "/game", description= "Начало игры"),
    ]
    await bot.set_my_commands(commands)
    
    # Включение обработчиков
    dp.include_routers(
        game.router, # Здесь все обработчики игры
        
        database_work.router, # А здесь все обработчики базы данных
        start.router, # Просто начальная информация о боте
    )
    dp.callback_query.outer_middleware(CallbackResponseMiddleware())

    # Начало работы
    logger.info("Бот начал работу")
    await dp.start_polling(bot, allowed_updates=["message", "inline_query", "chat_member", "my_chat_member", "callback_query"])
    logger.info("Бот закончил работу")

if __name__ == "__main__":
    asyncio.run(main())