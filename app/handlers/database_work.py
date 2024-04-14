# библиотеки
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import State, StatesGroup

# свои модули
from bot import logger
from app.database import DataBase


# Переменные для оргиназации работы
router = Router() # маршрутизатор
db = DataBase() # база данных

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
    kb.button(text= "Админы", callback_data= DataBaseCallbackFactory(table= "admins", action= "start"))
    kb.button(text= "Закрыть базу", callback_data= DataBaseCallbackFactory(table= "all", action= "end"))

    await message.answer("Выбери с какой таблицей хочешь поработать:", reply_markup= kb.as_markup())

@router.callback_query(DataBaseCallbackFactory.filter(F.admins == "all" and F.action == "begin"))
async def db_handler2(callback: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text= "Админы", callback_data= DataBaseCallbackFactory(table= "admins", action= "start"))
    kb.button(text= "Закрыть базу", callback_data= DataBaseCallbackFactory(table= "all", action= "end"))

    await callback.message.edit_text("Выбери с какой таблицей хочешь поработать:", reply_markup= kb.as_markup())

# Обработчик для закрытия базы
@router.callback_query(DataBaseCallbackFactory.filter(F.admins == "all" and F.action == "end"))
async def admins_handler(callback: CallbackQuery):
    db.close()
    await callback.message.edit_text("База закрыта")
    
    
# Обработчик для предоставления команд на взаимодействие с таблицей Admins
@router.callback_query(DataBaseCallbackFactory.filter(F.admins == "admins" and F.action == "start"))
async def admins_handler(callback: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text= "Добавить", callback_data= DataBaseCallbackFactory(table= "admins", action= "create"))
    kb.button(text= "Прочитать", callback_data= DataBaseCallbackFactory(table= "admins", action= "read"))
    kb.button(text= "Обновить", callback_data= DataBaseCallbackFactory(table= "admins", action= "update"))
    kb.button(text= "Удалить", callback_data= DataBaseCallbackFactory(table= "admins", action= "delete"))
    kb.button(text= "Назад", callback_data= DataBaseCallbackFactory(table= "all", action= "begin"))
    kb.adjust(4)
    
    
    await callback.message.edit_text("Выбери с какой таблицей хочешь поработать:", reply_markup= kb.as_markup())


# 
# Далее идет CRUD на Admins
# 
# Обработчик на чтение Admins
@router.callback_query(DataBaseCallbackFactory.filter(F.admins == "admins" and F.action == "read"))
async def read_admin_handler(callback: CallbackQuery):
    admins = db.admins.read(callback.from_user.id)

    if not admins:
        return callback.message.answer("База пуста")

    response = '\n'.join([f'ID: {admin[0]}    nickname: {admin[1]}' for admin in admins])
    await callback.message.answer(response)

# Обработчик для подготовки к добавлению в Admins
@router.callback_query(DataBaseCallbackFactory.filter(F.admins == "admins" and F.action == "create"))
async def prepare_create_admin_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Укажи ID и nickname.\nПример: 1 Ivan")
    await state.set_state(DataBaseStates.Admins.choosing_create)

# Обработчик на добавление в Admins
@router.message(DataBaseStates.Admins.choosing_create)
async def prepare_create_admin_handler(message: Message, state: FSMContext):
    id, nickname = message.text.split()

    if db.admins.create(message.from_user.id, id, nickname):
        await message.answer("Админ успешно добавлен")
    else:
        await message.answer("Произошла какая-то ошибка")

# Обработчик для подготовки к обновлению в Admins
@router.callback_query(DataBaseCallbackFactory.filter(F.admins == "admins" and F.action == "update"))
async def prepare_update_admin_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Укажи ID и новый Nickname \nПример: 1 Ivan")
    await state.set_state(DataBaseStates.Admins.choosing_update)

# Обработчик на обновление в Admins
@router.message(DataBaseStates.Admins.choosing_update)
async def prepare_update_admin_handler(message: Message, state: FSMContext):
    id, nickname = message.text.split()

    if db.admins.update(message.from_user.id, id, nickname):
        await message.answer("Админ успешно изменен")
    else:
        await message.answer("Произошла какая-то ошибка")

# Обработчик для подготовки к обновлению в Admins
@router.callback_query(DataBaseCallbackFactory.filter(F.admins == "admins" and F.action == "delete"))
async def prepare_delete_admin_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Укажи ID. \nПример: 1")
    await state.set_state(DataBaseStates.Admins.choosing_delete)

# Обработчик на обновление в Admins
@router.message(DataBaseStates.Admins.choosing_delete)
async def prepare_delete_admin_handler(message: Message, state: FSMContext):
    id, = message.text.split()

    if db.admins.delete(message.from_user.id, id):
        await message.answer("Админ успешно удален")
    else:
        await message.answer("Произошла какая-то ошибка")