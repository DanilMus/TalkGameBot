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
from app.messages import Messages
from app.callbacks import DatabaseCallbackFactory
from app.states import AdminsStates
from app.handlers.database_handlers.database_handlers_base import DatabaseHandlersBase
from config.config_reader import config



# Переменные для оргиназации работы
logger = logging.getLogger(__name__) # логирование событий
router = Router() # маршрутизатор
messages = Messages(__file__) # текст программы
handlers = DatabaseHandlersBase(__file__)


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
        if user.id != config.id_owner.get_secret_value():
            await event.answer(messages.take("no_rules"))
            return
        
        return await handler(event, data)

router.message.outer_middleware(IsCreatorMiddleware())
router.callback_query.outer_middleware(IsCreatorMiddleware())
        



#
# | Create | 
#

# Обработчик для подготовки к добавлению в Admins
@router.callback_query(DatabaseCallbackFactory.filter(F.table == handlers.table_name), DatabaseCallbackFactory.filter(F.action == "create"))
async def prepare_create_Admins_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(messages.take("example"))
    await state.set_state(AdminsStates.choosing_create)

# Обработчик на добавление в Admins
@router.message(AdminsStates.choosing_create)
async def create_Admins_handler(message: Message):
    id, username = message.text.split()
    await handlers.create_handler(message, id= id, username= username)



# 
# | Read |
# 

# Обработчик на чтение Admins
@router.callback_query(DatabaseCallbackFactory.filter(F.table == handlers.table_name), DatabaseCallbackFactory.filter(F.action == "read"))
async def read_Admins_handler(callback: CallbackQuery):
    await handlers.read_hadler(callback)



# 
# | Update |
# 

# Обработчик для подготовки к обновлению в Admins
@router.callback_query(DatabaseCallbackFactory.filter(F.table == handlers.table_name), DatabaseCallbackFactory.filter(F.action == "update"))
async def prepare_update_Admins_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(messages.take("example"))
    await state.set_state(AdminsStates.choosing_update)

# Обработчик на обновление в Admins
@router.message(AdminsStates.choosing_update)
async def update_Admins_handler(message: Message):
    id, username = message.text.split()
    await handlers.update_handler(message, id= id, username= username)


# 
# | Delete |
# 

# Обработчик для подготовки к удалению в Admins
@router.callback_query(DatabaseCallbackFactory.filter(F.table == handlers.table_name), DatabaseCallbackFactory.filter(F.action == "delete"))
async def prepare_delete_Admins_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(messages.take("example_toDel"))
    await state.set_state(AdminsStates.choosing_delete)

# Обработчик на удаление в Admins
@router.message(AdminsStates.choosing_delete)
async def delete_Admins_handler(message: Message):
    await handlers.delete_handler(message)