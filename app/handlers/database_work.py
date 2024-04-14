# библиотеки
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
# свои модули
from app.database import DataBase


# Переменные для оргиназации работы
router = Router() # маршрутизатор
db = DataBase() # база данных

# Класс для управления колбэками
class DataBaseCallbackFactory(CallbackData):
    table: str
    action: str

# обработчик для начала взаимодействия с лабой
@router.message(Command("db"))
async def db_handler(message: Message, state: FSMContext):
    await state.clear()

    buttons = [
        InlineKeyboardButton("Админы", callback_data= DataBaseCallbackFactory(table= "admins", action= "start"))
    ]
    kb = InlineKeyboardBuilder(inline_keyboard = buttons)
    await message.answer("Выбери с какой таблицей хочешь поработать:", reply_markup= kb)

    
# обработчик на взаимодействие с таблицей Admins
@router.callback_query(DataBaseCallbackFactory.filter(F.action == "start"))
async def admins_handler(callback: CallbackQuery, state: FSMContext):
    buttons = [
        InlineKeyboardButton("Добавить", callback_data= DataBaseCallbackFactory(table= "admins", action= "add")),
        InlineKeyboardButton("Прочитать", callback_data= DataBaseCallbackFactory(table= "admins", action= "read")),
        InlineKeyboardButton("Обновить", callback_data= DataBaseCallbackFactory(table= "admins", action= "update")),
        InlineKeyboardButton("Удалить", callback_data= DataBaseCallbackFactory(table= "admins", action= "delete"))
    ]
    kb = InlineKeyboardBuilder(inline_keyboard = buttons)
    await callback.answer("Выбери с какой таблицей хочешь поработать:", reply_markup= kb)