# 
# | Начало работы |
# 

# Библиотеки
from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

import logging

# Общение с пользователем
from app.messages import Messages
from app.database import async_session, DataBase


# Переменные для оргиназации работы
logger = logging.getLogger(__name__) # логирование событий
router = Router() # маршрутизатор
messages = Messages(__file__) # класс с диалогами



# Ставим Фильтр на действие только внутри частных чатов
router.message.filter(F.chat.type == "private") 
router.callback_query.filter(F.chat.type == "private") 


# Обработчик на банальное начало всего
@router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    # Добавляем нового игрока в базу, если его нет
    async with async_session() as session:
        gamers_db = DataBase.Gamers(session)
        if not await gamers_db.is_exists(message.from_user.id):
            await gamers_db.create(message.from_user.id, message.from_user.username)

    await state.clear() # сбрасываение состояний

    await message.answer(messages.take("start"))

# Обработчик на доп инфу
@router.message(Command("info"))
async def start_handler(message: Message, state: FSMContext):
    await state.clear() # сбрасываение состояний
    await message.answer(messages.take("info"))

# Обрабочик ситуации, когда игрок посылает что-то не в тему
# @router.message(F.text)
# async def problem_handler(message: Message, state: FSMContext):
#     await message.answer(messages.take("problem"))

