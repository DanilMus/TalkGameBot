from aiogram.types import Message, CallbackQuery

import logging

# Cвои модули
from app.database import DataBase, async_session
from app.dialog import Dialog

# Переменные для оргиназации работы
logger = logging.getLogger(__name__) # логирование событий

class DatabaseHandlers_Base:
    def __init__(self, Model: DataBase, dialog: Dialog):
        self.Model = Model
        self.dialog = dialog
        
    
    #
    # | Create | 
    #
    async def create_handler(self, message: Message, **kwargs):
        async with async_session() as session:
            table_db = self.Model(session)

            if await table_db.create(**kwargs): 
                return await message.answer(self.dialog.take("created"))
            
        await message.answer(self.dialog.take("error"))
    
    # 
    # | Read |
    # 
    async def read_hadler(self, callback: CallbackQuery):
        async with async_session() as session:
            table_db = self.Model(session)
            table_data = await table_db.read_all()

            if not table_data: # Проверка на пустоту
                return await callback.message.answer(self.dialog.take("base_empty"))
            
            response = '\n'.join([self.dialog.take("read") % data for data in table_data])
            await callback.message.answer(response)

    # 
    # | Update |
    # 
    async def update_handler(self, message: Message, id, **kwargs):
        async with async_session() as session:
            table_db = self.Model(session)
            if await table_db.update(id, **kwargs):
                return await message.answer(self.dialog.take("updated"))
            
        await message.answer(self.dialog.take("error"))

    # 
    # | Delete |
    # 
    async def delete_handler(self, message: Message):
        id, = message.text.split()

        async with async_session() as session:
            table_db = self.Model(session)
            if await table_db.delete(id):
                return await message.answer(self.dialog.take("deleted"))
            
        await message.answer(self.dialog.take("error"))


