"""|Read на Answers|"""

from aiogram import F, Router
from aiogram.types import CallbackQuery

import logging

# свои модули
from app.callbacks_factories import DatabaseCallbackFactory
from app.handlers.database_handlers.base import DatabaseHandlersBase



"""Переменные для оргиназации работы"""
logger = logging.getLogger(__name__) # логирование событий
router = Router() # маршрутизатор
handlers = DatabaseHandlersBase(__file__) # основа для хэндлеров


"""| Read |"""
@router.callback_query(DatabaseCallbackFactory.filter(F.table == handlers.table_name), DatabaseCallbackFactory.filter(F.action == "read"))
async def read_Answers_handler(callback: CallbackQuery, callback_data: DatabaseCallbackFactory):
    """Обработчик на чтение Answers
    """    
    await handlers.read_hadler(callback, callback_data)