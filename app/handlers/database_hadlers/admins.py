# 
# |CRUD на Admins|
# 


# библиотеки
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import logging

# свои модули
from app.dialog import Dialog
from app.database import db
from app.callbacks import DataBaseCallbackFactory



# Переменные для оргиназации работы
logger = logging.getLogger(__name__) # логирование событий
router = Router() # маршрутизатор
dialog = Dialog(Dialog.database_handlers.admins) # текст программы


# Класс для управления состояниями
class AdminsStates(StatesGroup):
    choosing_create = State()
    choosing_update = State()
    choosing_delete = State()



# Обработчик на чтение Admins
@router.callback_query(DataBaseCallbackFactory.filter(F.table == "Admins"), DataBaseCallbackFactory.filter(F.action == "read"))
async def read_admins_handler(callback: CallbackQuery):
    admins = db.admins.read()

    if not admins:
        return await callback.message.answer(dialog.take("base_empty"))

    response = '\n'.join([dialog.take("read") % admin for admin in admins])
    await callback.message.answer(response)



# Обработчик для подготовки к добавлению в Admins
@router.callback_query(DataBaseCallbackFactory.filter(F.table == "Admins"), DataBaseCallbackFactory.filter(F.action == "create"))
async def prepare_create_admins_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(dialog.take("example"))
    await state.set_state(AdminsStates.choosing_create)

# Обработчик на добавление в Admins
@router.message(AdminsStates.choosing_create)
async def prepare_create_admins_handler(message: Message, state: FSMContext):
    id, nickname = message.text.split()

    if db.admins.create(id, nickname):
        await message.answer(dialog.take("created"))
    else:
        await message.answer(dialog.take("error"))



# Обработчик для подготовки к обновлению в Admins
@router.callback_query(DataBaseCallbackFactory.filter(F.table == "Admins"), DataBaseCallbackFactory.filter(F.action == "update"))
async def prepare_update_admins_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(dialog.take("example"))
    await state.set_state(AdminsStates.choosing_update)

# Обработчик на обновление в Admins
@router.message(AdminsStates.choosing_update)
async def prepare_update_admins_handler(message: Message, state: FSMContext):
    id, nickname = message.text.split()

    if db.admins.update(id, nickname):
        await message.answer(dialog.take("updated"))
    else:
        await message.answer(dialog.take("error"))



# Обработчик для подготовки к удалению в Admins
@router.callback_query(DataBaseCallbackFactory.filter(F.table == "Admins"), DataBaseCallbackFactory.filter(F.action == "delete"))
async def prepare_delete_admins_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(dialog.take("example_toDel"))
    await state.set_state(AdminsStates.choosing_delete)

# Обработчик на удаление в Admins
@router.message(AdminsStates.choosing_delete)
async def prepare_delete_admins_handler(message: Message, state: FSMContext):
    id, = message.text.split()

    if db.admins.delete(id):
        await message.answer(dialog.take("deleted"))
    else:
        await message.answer(dialog.take("error"))