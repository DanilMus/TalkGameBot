# 
# |Обработчики для выбора с какой базой работать|
# 

# библиотеки
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

import logging

# свои модули
from app.dialog import Dialog
from app.database import db
from app.callbacks import DataBaseCallbackFactory
from app.handlers.database_hadlers import gamers, admins, games, questions_actions, questions_actions_from_gamers
from config import bot_config


# Переменные для оргиназации работы
logger = logging.getLogger(__name__) # логирование событий
router = Router() # маршрутизатор
dialog = Dialog(Dialog.database_work) # текст программы
# Подключение роутеров на обработку CRUD у различных таблиц
router.include_router(gamers.router)
router.include_router(admins.router)
router.include_router(games.router)
router.include_router(questions_actions.router)
router.include_router(questions_actions_from_gamers.router)


# Клавиатура для обработчиков db_handler и db_handler2
def kb_for_db_handler() -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.button(text= "Игроки", callback_data= DataBaseCallbackFactory(table= "Gamers", action= "start"))
    kb.button(text= "Админы", callback_data= DataBaseCallbackFactory(table= "Admins", action= "start"))
    kb.button(text= "Игры", callback_data= DataBaseCallbackFactory(table= "Games", action= "start"))
    kb.button(text= "Вопросы и Действия", callback_data= DataBaseCallbackFactory(table= "Questions_Actions", action= "start"))
    kb.button(text= "Вопросы и Действия от игроков", callback_data= DataBaseCallbackFactory(table= "Questions_Actions_From_Gamers", action= "start"))
    kb.button(text= "Закрыть базу", callback_data= DataBaseCallbackFactory(table= "all", action= "end"))
    kb.adjust(2)

    return kb

# Обработчик для начала взаимодействия с базой
@router.message(Command("db"))
async def db_handler(message: Message):
    db.connect()

    if not db.admins.is_exists(message.from_user.id):
        return await message.answer(dialog.take("no_rules"))

    await message.answer(dialog.take("what_table"), reply_markup= kb_for_db_handler().as_markup())

# Обработчик при нажатии кнопки "Назад"
@router.callback_query(DataBaseCallbackFactory.filter(F.table == "all" and F.action == "begin"))
async def db_handler2(callback: CallbackQuery):
    await callback.message.edit_text(dialog.take("what_table"), reply_markup= kb_for_db_handler().as_markup())



# Обработчик для закрытия базы
@router.callback_query(DataBaseCallbackFactory.filter(F.table == "all" and F.action == "end"))
async def admins_handler(callback: CallbackQuery):
    db.close()
    await callback.message.edit_text(dialog.take("base_close"))
    
    


# Обработчик для предоставления команд на взаимодействие с таблицами
@router.callback_query(DataBaseCallbackFactory.filter(F.action == "start"))
async def admins_handler(callback: CallbackQuery, callback_data: DataBaseCallbackFactory):
    table = callback_data.table

    if table == "Admins" and bot_config.creator != callback.from_user.id:
        callback_data= DataBaseCallbackFactory(table= "all", action= "begin")
        return await callback.message.answer(dialog.take("no_rules"))

    kb = InlineKeyboardBuilder()
    if table == "Admins" or table == "Questions_Actions": # Только у этих таблиц есть возможность редактирования
        kb.button(text= "Добавить", callback_data= DataBaseCallbackFactory(table= table, action= "create"))
        kb.button(text= "Прочитать", callback_data= DataBaseCallbackFactory(table= table, action= "read"))
        kb.button(text= "Обновить", callback_data= DataBaseCallbackFactory(table= table, action= "update"))
        kb.button(text= "Удалить", callback_data= DataBaseCallbackFactory(table= table, action= "delete"))
        kb.button(text= "Назад", callback_data= DataBaseCallbackFactory(table= "all", action= "begin"))
        kb.adjust(4)
    else:
        kb.button(text= "Прочитать", callback_data= DataBaseCallbackFactory(table= table, action= "read"))
        kb.button(text= "Назад", callback_data= DataBaseCallbackFactory(table= "all", action= "begin"))

    
    await callback.message.edit_text(dialog.take("what_action") % table, reply_markup= kb.as_markup())
