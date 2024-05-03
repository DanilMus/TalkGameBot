# 
# |Read на Answers|
# 


# библиотеки
from aiogram import F, Router
from aiogram.types import CallbackQuery

import logging

# свои модули
from app.dialog import Dialog
from app.database import DataBase
from app.callbacks import DataBaseCallbackFactory



# Переменные для оргиназации работы
logger = logging.getLogger(__name__) # логирование событий
router = Router() # маршрутизатор
dialog = Dialog(Dialog.database_handlers.answers) # текст программы



# 
# | Read |
# 

# Обработчик на чтение Answers
@router.callback_query(DataBaseCallbackFactory.filter(F.table == "Answers"), DataBaseCallbackFactory.filter(F.action == "read"))
async def read_Answers_handler(callback: CallbackQuery):
    async with DataBase.Answers() as answers:
        answers = await answers.read()

    if not answers:
        return await callback.message.answer(dialog.take("base_empty"))

    response = '\n'.join([dialog.take("read") % answer for answer in answers])
    await callback.message.answer(response)