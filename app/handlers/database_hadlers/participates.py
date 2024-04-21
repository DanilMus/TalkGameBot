# 
# |CRUD на Participates|
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
dialog = Dialog(Dialog.database_handlers.participates) # текст программы


# Обработчик на чтение Participates
@router.callback_query(DataBaseCallbackFactory.filter(F.table == "Participates"), DataBaseCallbackFactory.filter(F.action == "read"))
async def read_Participates_handler(callback: CallbackQuery):
    participates = db.participates.read()

    if not participates:
        return await callback.message.answer(dialog.take("base_empty"))

    response = '\n'.join([dialog.take("read") % partipate for partipate in participates])
    await callback.message.answer(response)