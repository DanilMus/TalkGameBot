# 
# |CRUD на Questions_Actions_From_Gamers|
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
dialog = Dialog(Dialog.database_handlers.questions_actions_from_gamers) # текст программы


# Обработчик на чтение Questions_Actions_From_Gamers
@router.callback_query(DataBaseCallbackFactory.filter(F.table == "Questions_Actions_From_Gamers"), DataBaseCallbackFactory.filter(F.action == "read"))
async def read_questions_actions_from_gamers_handler(callback: CallbackQuery):
    questions_actions_from_gamers = db.questions_actions_from_gamers.read()

    if not questions_actions_from_gamers:
        return await callback.message.answer(dialog.take("base_empty"))

    response = '\n'.join([dialog.take("read") % question_action for question_action in questions_actions_from_gamers])
    await callback.message.answer(response)