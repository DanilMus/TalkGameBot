from aiogram.types import Message, CallbackQuery

import logging

# Cвои модули
from app.database import DataBase, async_session
from app.messages import Messages

# Переменные для оргиназации работы
logger = logging.getLogger(__name__) # логирование событий

class DatabaseHandlers_Base:
    def __init__(self, Model: DataBase, messages: Messages):
        self.Model = Model
        self.messages = messages
        
    
    #
    # | Create | 
    #
    async def create_handler(self, message: Message, **kwargs):
        async with async_session() as session:
            table_db = self.Model(session)

            if await table_db.create(**kwargs): 
                return await message.answer(self.messages.take("created"))
            
        await message.answer(self.messages.take("error"))
    
    # 
    # | Read |
    # 
    async def read_hadler(self, callback: CallbackQuery):
        async with async_session() as session:
            table_db = self.Model(session)
            table_data = await table_db.read_all()

            if not table_data: # Проверка на пустоту
                return await callback.message.answer(self.messages.take("base_empty"))
            
            
            attributes = [column.name for column in table_db.model.__table__.columns]
            response = "\n".join([
                self.messages.take("read") % tuple(getattr(data, attr) for attr in attributes)
                for data in table_data
            ])
            await callback.message.answer(response)

    # 
    # | Update |
    # 
    async def update_handler(self, message: Message, id, **kwargs):
        async with async_session() as session:
            table_db = self.Model(session)
            if await table_db.update(id, **kwargs):
                return await message.answer(self.messages.take("updated"))
            
        await message.answer(self.messages.take("error"))

    # 
    # | Delete |
    # 
    async def delete_handler(self, message: Message):
        id, = message.text.split()

        async with async_session() as session:
            table_db = self.Model(session)
            if await table_db.delete(id):
                return await message.answer(self.messages.take("deleted"))
            
        await message.answer(self.messages.take("error"))


