""" | Файл с классом обработчиков для БД | """

from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

import logging
import os

# Cвои модули
from app.states import AdminsStates
from app.database import DataBase, async_session
from app.messages import Messages
from app.callbacks_factories import DatabaseCallbackFactory

"""Переменные для оргиназации работы"""
logger = logging.getLogger(__name__) # логирование событий


class DatabaseHandlersBase:
    """Класс - база для всех хэндлеров, которые обрабатывают взаимодействие с базой
    """    
    def __init__(self, for_file: str, Model: DataBase):
        self.messages = Messages(for_file)

        filename = os.path.basename(for_file)
        model_name = "_".join([el.capitalize() for el in os.path.splitext(filename)[0].split("_")])
        self.Model = getattr(DataBase, model_name)
        
    
    #
    # | Create | 
    #
    async def prepare_create_handler(self, callback: CallbackQuery, state: FSMContext):
        await callback.message.answer(self.messages.take("example"))
        await state.set_state(AdminsStates.choosing_create)

    async def create_handler(self, message: Message, **kwargs):
        async with async_session() as session:
            table_db = self.Model(session)

            if await table_db.create(**kwargs): 
                return await message.answer(self.messages.take("created"))
            
        await message.edit_text(self.messages.take("error"))
    
    # 
    # | Read |
    # 
    async def read_hadler(self, callback: CallbackQuery, callback_data: DatabaseCallbackFactory):
        async with async_session() as session:
            table_db = self.Model(session)
            
            if not await table_db.length(): # Проверка на пустоту
                return await callback.message.edit_text(self.messages.take("base_empty"))


            table_data = await table_db.read_by_page(callback_data.read_page)
            
            attributes = [column.name for column in table_db.model.__table__.columns]
            response = "\n".join([
                self.messages.take("read") % tuple(getattr(data, attr) for attr in attributes)
                for data in table_data
            ])

            keyboard = InlineKeyboardBuilder()
            if callback_data.read_page > 0:
                keyboard.button(text= "<", callback_data= DatabaseCallbackFactory(table= callback_data.table, action= callback_data.action, read_page= callback_data.read_page-1))
            if (callback_data.read_page+1)*5 < await table_db.length():
                keyboard.button(text= ">", callback_data= DatabaseCallbackFactory(table= callback_data.table, action= callback_data.action, read_page= callback_data.read_page+1))

            await callback.message.edit_text(response, reply_markup= keyboard.as_markup())

    # 
    # | Update |
    # 
    async def update_handler(self, message: Message, id, **kwargs):
        async with async_session() as session:
            table_db = self.Model(session)
            if await table_db.update(id, **kwargs):
                return await message.answer(self.messages.take("updated"))
            
        await message.edit_text(self.messages.take("error"))

    # 
    # | Delete |
    # 
    async def delete_handler(self, message: Message):
        id, = message.text.split()

        async with async_session() as session:
            table_db = self.Model(session)
            if await table_db.delete(id):
                return await message.answer(self.messages.take("deleted"))
            
        await message.edit_text(self.messages.take("error"))


