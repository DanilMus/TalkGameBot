# 
# |Read на Answers|
# 


# библиотеки
from aiogram import F, Router
from aiogram.types import CallbackQuery

import logging

# свои модули
from app.callbacks_factories import DatabaseCallbackFactory
from app.handlers.database_handlers.database_handlers_base import DatabaseHandlersBase



# Переменные для оргиназации работы
logger = logging.getLogger(__name__) # логирование событий
router = Router() # маршрутизатор
handlers = DatabaseHandlersBase(__file__)


# 
# | Read |
# 

# Обработчик на чтение Answers
@router.callback_query(DatabaseCallbackFactory.filter(F.table == handlers.table_name), DatabaseCallbackFactory.filter(F.action == "read"))
async def read_Answers_handler(callback: CallbackQuery):
    await handlers.read_hadler(callback)