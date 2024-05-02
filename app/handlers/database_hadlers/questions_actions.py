# 
# |CRUD на Questions_Actions|
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
dialog = Dialog(Dialog.database_handlers.questions_actions) # текст программы


# Класс для управления состояниями
class Questions_ActionsStates(StatesGroup):
    choosing_create = State()
    choosing_update = State()
    choosing_delete = State() 



#
# | Create | 
#

# Обработчик для подготовки к добавлению в Questions_Actions
@router.callback_query(DataBaseCallbackFactory.filter(F.table == "Questions_Actions"), DataBaseCallbackFactory.filter(F.action == "create"))
async def prepare_create_admin_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(dialog.take("example"))
    await state.set_state(Questions_ActionsStates.choosing_create)

# Обработчик на добавление в Questions_Actions
@router.message(Questions_ActionsStates.choosing_create)
async def prepare_create_admin_handler(message: Message, state: FSMContext):
    question_or_action, category, task = message.text.split("_")

    if await db.questions_actions.create(message.from_user.id, bool(int(question_or_action)), category, task): # Проверка на выполение запроса
        await message.answer(dialog.take("created"))
    else:
        await message.answer(dialog.take("error"))



# 
# | Read |
# 

# Обработчик на чтение Questions_Actions
@router.callback_query(DataBaseCallbackFactory.filter(F.table == "Questions_Actions"), DataBaseCallbackFactory.filter(F.action == "read"))
async def read_question_action_handler(callback: CallbackQuery):
    questions_actions = await db.questions_actions.read()

    if not questions_actions: # Проверка на пустоту и выполнения запроса
        return await callback.message.answer(dialog.take("base_empty"))

    response = '\n'.join([dialog.take("read") % question_action for question_action in questions_actions])
    await callback.message.answer(response)



# 
# | Update |
# 

# Обработчик для подготовки к обновлению в Questions_Actions
@router.callback_query(DataBaseCallbackFactory.filter(F.table == "Questions_Actions"), DataBaseCallbackFactory.filter(F.action == "update"))
async def prepare_update_admin_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(dialog.take("example_toUpdate"))
    await state.set_state(Questions_ActionsStates.choosing_update)

# Обработчик на обновление в Questions_Actions
@router.message(Questions_ActionsStates.choosing_update)
async def prepare_update_admin_handler(message: Message, state: FSMContext):
    id, question_or_action, category, task = message.text.split("_")

    if await db.questions_actions.update(message.from_user.id, id, bool(int(question_or_action)), category, task): # Проверка на выполнения запроса
        await message.answer(dialog.take("updated"))
    else:
        await message.answer(dialog.take("error"))




# 
# | Delete |
# 

# Обработчик для подготовки к удалению в Questions_Actions
@router.callback_query(DataBaseCallbackFactory.filter(F.table == "Questions_Actions"), DataBaseCallbackFactory.filter(F.action == "delete"))
async def prepare_delete_admin_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(dialog.take("example_toDel"))
    await state.set_state(Questions_ActionsStates.choosing_delete)

# Обработчик на удаление в Questions_Actions
@router.message(Questions_ActionsStates.choosing_delete)
async def prepare_delete_admin_handler(message: Message, state: FSMContext):
    id, = message.text.split()

    if await db.questions_actions.delete(id): # Проверка на выполнения запроса
        await message.answer(dialog.take("deleted"))
    else:
        await message.answer(dialog.take("error"))