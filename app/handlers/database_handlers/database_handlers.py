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
messages = Messages(__file__)


"""Хэндлеры"""
@router.callback_query(DatabaseCallbackFactory.filter(F.action == "start"))
async def admins_handler(callback: CallbackQuery, callback_data: DatabaseCallbackFactory, state: FSMContext):
    """Обработчик для предоставления команд на взаимодействие с таблицами
    """    
    await state.clear()
    table = callback_data.get_table_class()
    await state.update_data(
        handlers_base = DatabaseHandlersBase(
            for_file= __file__.replace("database_handlers.py", f"{callback_data.table.lower()}.py"), 
            Model= callback_data.get_table_class()
            )
        )

    kb = InlineKeyboardBuilder()
    if table is DataBase.Admins or table is DataBase.Questions_Actions: # Только у этих таблиц есть возможность редактирования
        kb.button(text= "Добавить", callback_data= DatabaseCallbackFactory(table= table, action= "create"))
        kb.button(text= "Прочитать", callback_data= DatabaseCallbackFactory(table= table, action= "read"))
        kb.button(text= "Обновить", callback_data= DatabaseCallbackFactory(table= table, action= "update"))
        kb.button(text= "Удалить", callback_data= DatabaseCallbackFactory(table= table, action= "delete"))
    else:
        kb.button(text= "Прочитать", callback_data= DatabaseCallbackFactory(table= table, action= "read"))
    kb.button(text= "Назад", callback_data= DatabaseCallbackFactory(action= "begin"))
    kb.adjust(4, 1)

    await callback.message.edit_text(messages.take("what_action") % callback_data.table, reply_markup= kb.as_markup())


"""| Create |"""
@router.callback_query(DatabaseCallbackFactory.filter(F.action == "create"))
async def prepare_create_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик для подготовки к добавлению в таблицу
    """    
    handlers_base = await state.get_data("handlers_base")
    await handlers_base.prepare_create_handler(callback, state)

@router.message(AdminsStates.choosing_create)
async def create_handler(message: Message, state: FSMContext):
    """Обработчик на добавление в таблицу
    """    
    handlers_base = await state.get_data("handlers_base")
    match handlers_base.Model:
        case DataBase.Admins:
            id, username = message.text.split()
            await handlers_base.create_handler(message, id= id, username= username)


"""| Read |"""
@router.callback_query(DatabaseCallbackFactory.filter(F.action == "read"))
async def read_handler(callback: CallbackQuery, callback_data: DatabaseCallbackFactory, state: FSMContext):
    """Обработчик на чтение Admins
    """    
    data = await state.get_data()
    handlers_base = data["handlers_base"]
    await handlers_base.read_hadler(callback, callback_data)