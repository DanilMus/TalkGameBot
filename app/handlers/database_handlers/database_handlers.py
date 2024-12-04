"""| CRUD на все таблицы |"""


from aiogram import F, Router, BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from aiogram.fsm.context import FSMContext

import logging
from typing import Any, Callable, Dict, Awaitable

# Свои модули
from app.messages import Messages
from app.callbacks_factories import DatabaseCallbackFactory
from app.states import AdminsStates
from app.handlers.database_handlers.base import DatabaseHandlersBase
from config.config_reader import config


"""Переменные для оргиназации работы"""
logger = logging.getLogger(__name__) # логирование событий
router = Router() # маршрутизатор

"""| Create |"""
@router.callback_query(DatabaseCallbackFactory.filter(F.action == "create"))
async def prepare_create_Admins_handler(callback: CallbackQuery, state: FSMContext, callback_data: DatabaseCallbackFactory):
    await callback.message.answer(messages.take("example"))
    await state.set_state(AdminsStates.choosing_create)