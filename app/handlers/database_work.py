# библиотеки
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import State, StatesGroup

import logging

# свои модули
from app.dialog import Dialog
from app.database import DataBase


# Переменные для оргиназации работы
logger = logging.getLogger(__name__) # логирование событий
router = Router() # маршрутизатор
db = DataBase() # база данных
dialog = Dialog(Dialog.database_work) # текст программы

# Класс для управления колбэками
class DataBaseCallbackFactory(CallbackData, prefix= "db"):
    table: str
    action: str

# Класс для управления состояниями
class DataBaseStates(StatesGroup):
    class Admins(StatesGroup):
        choosing_create = State()
        choosing_update = State()
        choosing_delete = State()


# обработчик для начала взаимодействия с лабой
@router.message(Command("db"))
async def db_handler(message: Message):
    db.connect()

    kb = InlineKeyboardBuilder()
    kb.button(text= "Админы", callback_data= DataBaseCallbackFactory(table= "Admins", action= "start"))
    kb.button(text= "Закрыть базу", callback_data= DataBaseCallbackFactory(table= "all", action= "end"))

    await message.answer(dialog.take("what_table"), reply_markup= kb.as_markup())

@router.callback_query(DataBaseCallbackFactory.filter(F.table == "all" and F.action == "begin"))
async def db_handler2(callback: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text= "Админы", callback_data= DataBaseCallbackFactory(table= "Admins", action= "start"))
    kb.button(text= "Закрыть базу", callback_data= DataBaseCallbackFactory(table= "all", action= "end"))

    await callback.message.edit_text(dialog.take("what_table"), reply_markup= kb.as_markup())

# Обработчик для закрытия базы
@router.callback_query(DataBaseCallbackFactory.filter(F.table == "all" and F.action == "end"))
async def admins_handler(callback: CallbackQuery):
    db.close()
    await callback.message.edit_text(dialog.take("base_close"))
    
    
# Обработчик для предоставления команд на взаимодействие с таблицей Admins
@router.callback_query(DataBaseCallbackFactory.filter(F.action == "start"))
async def admins_handler(callback: CallbackQuery, callback_data: DataBaseCallbackFactory):
    table = callback_data.table
    kb = InlineKeyboardBuilder()
    kb.button(text= "Добавить", callback_data= DataBaseCallbackFactory(table=table, action= "create"))
    kb.button(text= "Прочитать", callback_data= DataBaseCallbackFactory(table=table, action= "read"))
    kb.button(text= "Обновить", callback_data= DataBaseCallbackFactory(table=table, action= "update"))
    kb.button(text= "Удалить", callback_data= DataBaseCallbackFactory(table=table, action= "delete"))
    kb.button(text= "Назад", callback_data= DataBaseCallbackFactory(table= "all", action= "begin"))
    kb.adjust(4)
    
    await callback.message.edit_text(dialog.take("what_action") % table, reply_markup= kb.as_markup())



# 
# Далее идет CRUD на Admins
# 
# Обработчик на чтение Admins
@router.callback_query(DataBaseCallbackFactory.filter(F.table == "Admins" and F.action == "read"))
async def read_admin_handler(callback: CallbackQuery):
    admins = db.admins.read(callback.from_user.id)

    if not admins:
        return callback.message.answer(dialog.take("base_empty"))

    response = '\n'.join([dialog.take("admin_read") % (admin[0], admin [1]) for admin in admins])
    await callback.message.answer(response)

# Обработчик для подготовки к добавлению в Admins
@router.callback_query(DataBaseCallbackFactory.filter(F.admins == "Admins" and F.action == "create"))
async def prepare_create_admin_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(dialog.take("admin_example"))
    await state.set_state(DataBaseStates.Admins.choosing_create)

# Обработчик на добавление в Admins
@router.message(DataBaseStates.Admins.choosing_create)
async def prepare_create_admin_handler(message: Message, state: FSMContext):
    id, nickname = message.text.split()

    if db.admins.create(message.from_user.id, id, nickname):
        await message.answer(dialog.take("admin_created"))
    else:
        await message.answer(dialog.take("error"))

# Обработчик для подготовки к обновлению в Admins
@router.callback_query(DataBaseCallbackFactory.filter(F.table == "Admins" and F.action == "update"))
async def prepare_update_admin_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(dialog.take("admin_example"))
    await state.set_state(DataBaseStates.Admins.choosing_update)

# Обработчик на обновление в Admins
@router.message(DataBaseStates.Admins.choosing_update)
async def prepare_update_admin_handler(message: Message, state: FSMContext):
    id, nickname = message.text.split()

    if db.admins.update(message.from_user.id, id, nickname):
        await message.answer(dialog.take("admin_updated"))
    else:
        await message.answer(dialog.take("error"))

# Обработчик для подготовки к обновлению в Admins
@router.callback_query(DataBaseCallbackFactory.filter(F.table == "Admins" and F.action == "delete"))
async def prepare_delete_admin_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(dialog.take("example_toDel"))
    await state.set_state(DataBaseStates.Admins.choosing_delete)

# Обработчик на обновление в Admins
@router.message(DataBaseStates.Admins.choosing_delete)
async def prepare_delete_admin_handler(message: Message, state: FSMContext):
    id, = message.text.split()

    if db.admins.delete(message.from_user.id, id):
        await message.answer(dialog.take("admin_deleted"))
    else:
        await message.answer(dialog.take("error"))