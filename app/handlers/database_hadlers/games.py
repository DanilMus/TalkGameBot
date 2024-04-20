# 
# |CRUD на Games|
# 


# библиотеки
from aiogram import F, Router
from aiogram.types import CallbackQuery

import logging

# свои модули
from app.dialog import Dialog
from app.database import db
from app.callbacks import DataBaseCallbackFactory



# Переменные для оргиназации работы
logger = logging.getLogger(__name__) # логирование событий
router = Router() # маршрутизатор
dialog = Dialog(Dialog.database_handlers.games) # текст программы


# Обработчик на чтение Games
@router.callback_query(DataBaseCallbackFactory.filter(F.table == "Games"), DataBaseCallbackFactory.filter(F.action == "read"))
async def read_games_handler(callback: CallbackQuery):
    games = db.games.read()

    if not games:
        return await callback.message.answer(dialog.take("base_empty"))

    response = '\n'.join([dialog.take("read") % game for game in games])
    await callback.message.answer(response)