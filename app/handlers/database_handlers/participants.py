# 
# |Read на Participants|
# 


# библиотеки
from aiogram import F, Router
from aiogram.types import CallbackQuery

import logging

# свои модули
from app.callbacks_factories import DatabaseCallbackFactory
from app.handlers.database_handlers.base import DatabaseHandlersBase



# Переменные для оргиназации работы
logger = logging.getLogger(__name__) # логирование событий
router = Router() # маршрутизатор
handlers = DatabaseHandlersBase(__file__)


# 
# | Read |
# 

# Обработчик на чтение Participants
@router.callback_query(DatabaseCallbackFactory.filter(F.table == handlers.table_name), DatabaseCallbackFactory.filter(F.action == "read"))
async def read_participants_handler(callback: CallbackQuery, callback_data: DatabaseCallbackFactory):
    await handlers.read_hadler(callback, callback_data)