# 
# | CRUD на Admins |
# 


# Библиотеки
from aiogram import F, Router, BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from aiogram.fsm.context import FSMContext

import logging
from typing import Any, Callable, Dict, Awaitable

# Свои модули
from app.dialog import Dialog
from app.database import DataBase, async_session
from app.callbacks import DataBaseCallbackFactory
from app.states import AdminsStates
from app.handlers.database_hadlers.database_handlers_base import DatabaseHandlers_Base
from config import config



# Переменные для оргиназации работы
logger = logging.getLogger(__name__) # логирование событий
router = Router() # маршрутизатор
dialog = Dialog(Dialog.database_handlers.admins) # текст программы
admins_handlers = DatabaseHandlers_Base(Model= DataBase.Admins, dialog= dialog)


# Outer-мидлварь на проверку прав доступа главного админа
class IsCreatorMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        user = data["event_from_user"]
        # Если это не админ или не главный админ, то не работаем с этим пользовалетелем
        if user.id != config.creator:
            await event.answer(dialog.take("no_rules"))
            return
        
        return await handler(event, data)

router.message.outer_middleware(IsCreatorMiddleware())
router.callback_query.outer_middleware(IsCreatorMiddleware())
        



#
# | Create | 
#

# Обработчик для подготовки к добавлению в Admins
@router.callback_query(DataBaseCallbackFactory.filter(F.table == "Admins"), DataBaseCallbackFactory.filter(F.action == "create"))
async def prepare_create_admins_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(dialog.take("example"))
    await state.set_state(AdminsStates.choosing_create)

# Обработчик на добавление в Admins
@router.message(AdminsStates.choosing_create)
async def create_admins_handler(message: Message):
    id, username = message.text.split()
    await admins_handlers.create_handler(message, id= id, username= username)



# 
# | Read |
# 

# Обработчик на чтение Admins
@router.callback_query(DataBaseCallbackFactory.filter(F.table == "Admins"), DataBaseCallbackFactory.filter(F.action == "read"))
async def read_admins_handler(callback: CallbackQuery):
    await admins_handlers.read_hadler(callback)



# 
# | Update |
# 

# Обработчик для подготовки к обновлению в Admins
@router.callback_query(DataBaseCallbackFactory.filter(F.table == "Admins"), DataBaseCallbackFactory.filter(F.action == "update"))
async def prepare_update_admins_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(dialog.take("example"))
    await state.set_state(AdminsStates.choosing_update)

# Обработчик на обновление в Admins
@router.message(AdminsStates.choosing_update)
async def update_admins_handler(message: Message):
    id, username = message.text.split()
    await admins_handlers.update_handler(message, id= id, username= username)


# 
# | Delete |
# 

# Обработчик для подготовки к удалению в Admins
@router.callback_query(DataBaseCallbackFactory.filter(F.table == "Admins"), DataBaseCallbackFactory.filter(F.action == "delete"))
async def prepare_delete_admins_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(dialog.take("example_toDel"))
    await state.set_state(AdminsStates.choosing_delete)

# Обработчик на удаление в Admins
@router.message(AdminsStates.choosing_delete)
async def delete_admins_handler(message: Message):
    await admins_handlers.delete_handler(message)