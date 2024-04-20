# 
# |CRUD на Gamers|
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
dialog = Dialog(Dialog.database_handlers.gamers) # текст программы


# Обработчик на чтение Gamers
@router.callback_query(DataBaseCallbackFactory.filter(F.table == "Gamers"), DataBaseCallbackFactory.filter(F.action == "read"))
async def read_gamers_handler(callback: CallbackQuery):
    gamers = db.gamers.read()

    if not gamers:
        return await callback.message.answer(dialog.take("base_empty"))

    response = '\n'.join([dialog.take("read") % gamer for gamer in gamers])
    await callback.message.answer(response)