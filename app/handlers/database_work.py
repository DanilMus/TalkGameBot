from aiogram import Dispatcher, types
from db import DataBase

# инициализация базы данных
database = DataBase()

async def on_admins_command(message: types.Message):
    # получение всех админов
    admins = database.admins.read_all()
    # форматирование списка админов для отправки в чат
    admins_text = "\n".join(f"{admin[0]}: {admin[1]}" for admin in admins)
    await message.reply(f"Админы:\n{admins_text}")

async def on_questions_actions_command(message: types.Message):
    # получение всех вопросов/действий
    questions_actions = database.questions_actions.read_all()
    # форматирование списка вопросов/действий для отправки в чат
    questions_actions_text = "\n".join(f"{qa[0]}: {qa[1]}" for qa in questions_actions)
    await message.reply(f"Вопросы/Действия:\n{questions_actions_text}")

# регистрация обработчиков
async def register_database_work(dp: Dispatcher):
    dp.message_handler(commands="admins")(on_admins_command)
    dp.message_handler(commands="questions_actions")(on_questions_actions_command)