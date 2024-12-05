"""| CRUD на все таблицы |"""


from aiogram import F, Router, BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

import logging
from typing import Any, Callable, Dict, Awaitable

# Свои модули
from app.messages import Messages
from app.callbacks_factories import DatabaseCallbackFactory
from app.states import AdminsStates
from app.database import DataBase
from app.handlers.database_handlers.base import DatabaseHandlersBase

from config.config_reader import config


"""Переменные для оргиназации работы"""
logger = logging.getLogger(__name__) # логирование событий
router = Router() # маршрутизатор
handlers_base = None


"""Хэндлеры"""
@router.callback_query(DatabaseCallbackFactory.filter(F.action == "start"))
async def admins_handler(callback: CallbackQuery, callback_data: DatabaseCallbackFactory, state: FSMContext):
    """Обработчик для предоставления команд на взаимодействие с таблицами
    """    
    await state.clear()
    table = callback_data.table
    handlers_base = DatabaseHandlersBase(__file__.replace(f"{table.__name__}"))

    kb = InlineKeyboardBuilder()
    if table is DataBase.Admins or table == DataBase.Questions_Actions: # Только у этих таблиц есть возможность редактирования
        kb.button(text= "Добавить", callback_data= DatabaseCallbackFactory(table= table, action= "create"))
        kb.button(text= "Прочитать", callback_data= DatabaseCallbackFactory(table= table, action= "read"))
        kb.button(text= "Обновить", callback_data= DatabaseCallbackFactory(table= table, action= "update"))
        kb.button(text= "Удалить", callback_data= DatabaseCallbackFactory(table= table, action= "delete"))
        kb.adjust(4)
    else:
        kb.button(text= "Прочитать", callback_data= DatabaseCallbackFactory(table= table, action= "read"))
    kb.button(text= "Назад", callback_data= DatabaseCallbackFactory(table= "all", action= "begin"))

    
    await callback.message.edit_text('messages.take("what_action") % table', reply_markup= kb.as_markup())


"""| Create |"""
@router.callback_query(DatabaseCallbackFactory.filter(F.action == "create"))
async def prepare_create_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик для подготовки к добавлению в таблицу
    """    
    await handlers_base.prepare_create_handler(callback, state)

@router.message(AdminsStates.choosing_create)
async def create_handler(message: Message):
    """Обработчик на добавление в таблицу
    """    
    match handlers_base.Model:
        case DataBase.Admins:
            id, username = message.text.split()
            await handlers_base.create_handler(message, id= id, username= username)


"""| Read |"""
@router.callback_query(DatabaseCallbackFactory.filter(F.action == "read"))
async def read_handler(callback: CallbackQuery, callback_data: DatabaseCallbackFactory):
    """Обработчик на чтение Admins
    """    
    await handlers_base.read_hadler(callback, callback_data)