# 
# | CRUD на Questions_Actions |
# 


# Библиотеки
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import logging

# Свои модули
from app.messages import Messages
from app.callbacks_factories import DatabaseCallbackFactory
from app.states import Questions_ActionsStates
from app.handlers.database_handlers.database_handlers_base import DatabaseHandlersBase



# Переменные для оргиназации работы
logger = logging.getLogger(__name__) # логирование событий
router = Router() # маршрутизатор
messages = Messages(__file__) # текст программы
handlers = DatabaseHandlersBase(__file__)
        



#
# | Create | 
#

# Обработчик для подготовки к добавлению в Questions_Actions
@router.callback_query(DatabaseCallbackFactory.filter(F.table == handlers.table_name), DatabaseCallbackFactory.filter(F.action == "create"))
async def prepare_create_Questions_Actions_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(messages.take("example"))
    await state.set_state(Questions_ActionsStates.choosing_create)

# Обработчик на добавление в Questions_Actions
@router.message(Questions_ActionsStates.choosing_create)
async def create_Questions_Actions_handler(message: Message):
    id_admin = message.from_user.id
    question_or_action, category, question_action = message.text.split("_")
    question_or_action = bool(int(question_or_action))
    await handlers.create_handler(message, id_admin= id_admin, question_or_action= question_or_action, category= category, question_action= question_action)



# 
# | Read |
# 

# Обработчик на чтение Questions_Actions
@router.callback_query(DatabaseCallbackFactory.filter(F.table == handlers.table_name), DatabaseCallbackFactory.filter(F.action == "read"))
async def read_Questions_Actions_handler(callback: CallbackQuery):
    await handlers.read_hadler(callback)



# 
# | Update |
# 

# Обработчик для подготовки к обновлению в Questions_Actions
@router.callback_query(DatabaseCallbackFactory.filter(F.table == handlers.table_name), DatabaseCallbackFactory.filter(F.action == "update"))
async def prepare_update_Questions_Actions_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(messages.take("example_toUpdate"))
    await state.set_state(Questions_ActionsStates.choosing_update)

# Обработчик на обновление в Questions_Actions
@router.message(Questions_ActionsStates.choosing_update)
async def update_Questions_Actions_handler(message: Message):
    id_admin = message.from_user.id
    id, question_or_action, category, question_action = message.text.split("_")
    id, question_or_action = int(id), bool(int(question_or_action))
    await handlers.update_handler(message, id= id, id_admin= id_admin, question_or_action= question_or_action, category= category, question_action= question_action)


# 
# | Delete |
# 

# Обработчик для подготовки к удалению в Questions_Actions
@router.callback_query(DatabaseCallbackFactory.filter(F.table == handlers.table_name), DatabaseCallbackFactory.filter(F.action == "delete"))
async def prepare_delete_Questions_Actions_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(messages.take("example_toDel"))
    await state.set_state(Questions_ActionsStates.choosing_delete)

# Обработчик на удаление в Questions_Actions
@router.message(Questions_ActionsStates.choosing_delete)
async def delete_Questions_Actions_handler(message: Message):
    await handlers.delete_handler(message)