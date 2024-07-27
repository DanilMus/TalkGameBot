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
from app.dialog import Dialog
from app.database import async_session, DataBase


# Переменные для оргиназации работы
logger = logging.getLogger(__name__) # логирование событий
router = Router() # маршрутизатор
dialog = Dialog(Dialog.start) # класс с диалогами



# Обработчик на команду start
@router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    # Добавляем нового игрока в базу, если его нет
    async with async_session() as session:
        gamers_db = DataBase.Gamers(session)
        if not await gamers_db.is_exists(message.from_user.id):
            await gamers_db.create(message.from_user.id, message.from_user.username)

    await state.clear() # сбрасываение состояний

    await message.answer(dialog.take("start"))

# Обрабочик ситуации, когда игрок посылает что-то не в тему
@router.message(F.text)
async def problem_handler(message: Message, state: FSMContext):
    await message.answer(dialog.take("problem"))

