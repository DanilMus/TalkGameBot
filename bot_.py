from config.config import token
from db import DataBase
from aiogram import Bot, Dispatcher, types

bot = Bot(token= token)
dp = Dispatcher(bot= bot)
db = DataBase()


@dp.message_handler(commands=['add_admin'])
async def add_admin(message: types.Message):
    id, nickname = message.text.split()[1:]
    db.admins.create(id, nickname)
    await message.answer("Админ добавлен")

@dp.message_handler(commands=['get_admins'])
async def get_admins(message: types.Message):
    admins = db.admins.read()
    response = '\n'.join([f'id: {admin[0]}, nickname: {admin[1]}' for admin in admins])
    await message.answer(response)

@dp.message_handler(commands=['update_admin'])
async def update_admin(message: types.Message):
    id, nickname = message.text.split()[1:]
    db.admins.update(id, nickname)
    await message.answer("Информация об админе обновлена")

@dp.message_handler(commands=['delete_admin'])
async def delete_admin(message: types.Message):
    id = message.text.split()[1]
    db.admins.delete(id)
    await message.answer("Админ удален")

@dp.message_handler(commands=['delete_all_admins'])
async def delete_all_admins(message: types.Message):
    db.admins.delete_all()
    await message.answer("Все админы удалены")
