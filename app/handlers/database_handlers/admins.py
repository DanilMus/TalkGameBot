"""| CRUD на Admins |"""


from aiogram import F, Router, BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from aiogram.fsm.context import FSMContext

import logging
from typing import Any, Callable, Dict, Awaitable

# Свои модули
from app.messages import Messages
from app.callbacks_factories import DatabaseCallbackFactory
from app.states import AdminsStates
from app.handlers.database_handlers.base import DatabaseHandlersBase
from config.config_reader import config



"""Переменные для оргиназации работы"""
logger = logging.getLogger(__name__) # логирование событий
router = Router() # маршрутизатор
messages = Messages(__file__) # текст программы
handlers = DatabaseHandlersBase(__file__)


"""Фильтры и Мидлвари"""
class IsCreatorMiddleware(BaseMiddleware):
    """Мидлварь на проверку прав доступа главного админа
    """    
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        """Вызов мидлвари для проверки

        Args:
            handler (Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]]): хэндлер, в котором произошел вызов
            event (TelegramObject): это какой-то ивент по типу message, callback...
            data (Dict[str, Any]): _description_

        Returns:
            Any: возвращает либо ничего, либо хэндлер, если проверка прошла удачно
        """        
        user = data["event_from_user"]
        
        # Если это не главный админ, то не работаем с этим пользовалетелем
        if user.id != config.id_owner.get_secret_value():
            await event.answer(messages.take("no_rules"))
            return
        
        return await handler(event, data)
# Подключение мидлвари к ивентам сообщений и колбэков
router.message.middleware(IsCreatorMiddleware())
router.callback_query.middleware(IsCreatorMiddleware())
        



"""| Create |"""
@router.callback_query(DatabaseCallbackFactory.filter(F.table == handlers.Model), DatabaseCallbackFactory.filter(F.action == "create"))
async def prepare_create_Admins_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик для подготовки к добавлению в Admins
    """    
    await callback.message.answer(messages.take("example"))
    await state.set_state(AdminsStates.choosing_create)

@router.message(AdminsStates.choosing_create)
async def create_Admins_handler(message: Message):
    """Обработчик на добавление в Admins
    """    
    id, username = message.text.split()
    await handlers.create_handler(message, id= id, username= username)



"""| Read |"""
@router.callback_query(DatabaseCallbackFactory.filter(F.table == handlers.Model), DatabaseCallbackFactory.filter(F.action == "read"))
async def read_Admins_handler(callback: CallbackQuery, callback_data: DatabaseCallbackFactory):
    """Обработчик на чтение Admins
    """    
    await handlers.read_hadler(callback, callback_data)



"""| Update |"""
@router.callback_query(DatabaseCallbackFactory.filter(F.table == handlers.Model), DatabaseCallbackFactory.filter(F.action == "update"))
async def prepare_update_Admins_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик для подготовки к обновлению в Admins
    """    
    await callback.message.answer(messages.take("example"))
    await state.set_state(AdminsStates.choosing_update)

@router.message(AdminsStates.choosing_update)
async def update_Admins_handler(message: Message):
    """Обработчик на обновление в Admins
    """    
    id, username = message.text.split()
    await handlers.update_handler(message, id= id, username= username)


"""| Delete |"""
@router.callback_query(DatabaseCallbackFactory.filter(F.table == handlers.Model), DatabaseCallbackFactory.filter(F.action == "delete"))
async def prepare_delete_Admins_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик для подготовки к удалению в Admins
    """    
    await callback.message.answer(messages.take("example_toDel"))
    await state.set_state(AdminsStates.choosing_delete)

@router.message(AdminsStates.choosing_delete)
async def delete_Admins_handler(message: Message):
    """Обработчик на удаление в Admins
    """    
    await handlers.delete_handler(message)